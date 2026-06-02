from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..repositories.sensor_repository import sensor_repository


class ReportService:
    BUCKET_SECONDS = 60
    EVENT_COOLDOWN_SECONDS = 300
    STATE_SEVERITY = {
        "EMPTY": 0,
        "ENTERING": 1,
        "ACTIVE": 2,
        "TOILET_USE": 3,
        "ABNORMAL": 4,
        "EMERGENCY": 5,
    }

    def build_weekly_report(self, days: int = 7) -> Dict[str, Any]:
        safe_days = max(1, min(days, 31))
        now = datetime.utcnow()
        period_start = now - timedelta(days=safe_days - 1)
        period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = now

        records = [
            record
            for record in sensor_repository.list_records(sensor="mmwave")
            if self._is_in_period(record.get("timestamp"), period_start, period_end)
        ]

        processed_records = self._preprocess_mmwave_records(records)

        daily = self._build_empty_daily(period_start, safe_days)
        zone_duration_seconds = {"toilet": 0, "sink": 0, "bath": 0, "unknown": 0}
        abnormal_events: List[Dict[str, Any]] = []
        detected_still_times: List[int] = []
        last_night_toilet_at: Optional[datetime] = None
        last_event_at: Dict[str, datetime] = {}

        totals = {
            "raw_record_count": len(records),
            "processed_record_count": len(processed_records),
            "detected_count": 0,
            "anomaly_count": 0,
            "fall_count": 0,
            "emergency_count": 0,
            "night_toilet_count": 0,
        }

        for record in processed_records:
            timestamp = self._parse_timestamp(record.get("timestamp"))
            if timestamp is None:
                continue

            date_key = timestamp.date().isoformat()
            day = daily.setdefault(date_key, self._empty_day(date_key))
            payload = record.get("payload") or {}
            status = record.get("status") or {}
            anomaly = record.get("anomaly") or {}
            fall_detection = record.get("fall_detection") or {}

            detected = bool(payload.get("detected"))
            zone = payload.get("zone") or "unknown"
            still_time = int(payload.get("still_time") or 0)
            current_state = status.get("current_state")
            anomaly_detected = bool(anomaly.get("detected"))
            fall_detected = bool(fall_detection.get("detected"))

            day["raw_record_count"] += int(record.get("raw_record_count") or 1)
            day["processed_record_count"] += 1
            day["zone_counts"][zone] = day["zone_counts"].get(zone, 0) + 1
            day["max_still_time_seconds"] = max(day["max_still_time_seconds"], still_time)

            if detected:
                totals["detected_count"] += 1
                day["detected_count"] += 1
                detected_still_times.append(still_time)
                zone_duration_seconds[zone if zone in zone_duration_seconds else "unknown"] += self.BUCKET_SECONDS

                if zone == "toilet" and (timestamp.hour >= 22 or timestamp.hour < 6):
                    if (
                        last_night_toilet_at is None
                        or (timestamp - last_night_toilet_at).total_seconds() > self.BUCKET_SECONDS
                    ):
                        totals["night_toilet_count"] += 1
                        day["night_toilet_count"] += 1
                    last_night_toilet_at = timestamp

            if anomaly_detected:
                totals["anomaly_count"] += 1
                day["anomaly_count"] += 1
                if self._should_emit_event("anomaly", timestamp, last_event_at):
                    abnormal_events.append(
                        self._event_summary(
                            timestamp=record.get("timestamp"),
                            event_type="anomaly",
                            level="warning",
                            zone=zone,
                            still_time=still_time,
                            reason=anomaly.get("reason"),
                        )
                    )

            if fall_detected:
                totals["fall_count"] += 1
                day["fall_count"] += 1
                if self._should_emit_event("fall", timestamp, last_event_at):
                    abnormal_events.append(
                        self._event_summary(
                            timestamp=record.get("timestamp"),
                            event_type="fall",
                            level="danger",
                            zone=zone,
                            still_time=still_time,
                            reason=fall_detection.get("reason"),
                        )
                    )

            if current_state == "EMERGENCY":
                totals["emergency_count"] += 1
                day["emergency_count"] += 1

        average_still_time = (
            round(sum(detected_still_times) / len(detected_still_times), 2)
            if detected_still_times
            else 0.0
        )

        return {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "days": safe_days,
            },
            "source": "raw_mmwave_records",
            "preprocessing": {
                "bucket_seconds": self.BUCKET_SECONDS,
                "event_cooldown_seconds": self.EVENT_COOLDOWN_SECONDS,
            },
            "summary": {
                **totals,
                "average_still_time_seconds": average_still_time,
                "zone_duration_seconds": zone_duration_seconds,
            },
            "daily": list(daily.values()),
            "abnormal_events": abnormal_events,
        }

    def _build_empty_daily(self, start: datetime, days: int) -> Dict[str, Dict[str, Any]]:
        return {
            (start + timedelta(days=index)).date().isoformat(): self._empty_day(
                (start + timedelta(days=index)).date().isoformat()
            )
            for index in range(days)
        }

    def _empty_day(self, date_key: str) -> Dict[str, Any]:
        return {
            "date": date_key,
            "raw_record_count": 0,
            "processed_record_count": 0,
            "detected_count": 0,
            "anomaly_count": 0,
            "fall_count": 0,
            "emergency_count": 0,
            "night_toilet_count": 0,
            "max_still_time_seconds": 0,
            "zone_counts": {},
        }

    def _preprocess_mmwave_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        buckets: Dict[datetime, List[Dict[str, Any]]] = {}
        for record in sorted(records, key=lambda item: item.get("timestamp") or ""):
            timestamp = self._parse_timestamp(record.get("timestamp"))
            if timestamp is None:
                continue
            bucket_time = timestamp.replace(
                second=(timestamp.second // self.BUCKET_SECONDS) * self.BUCKET_SECONDS,
                microsecond=0,
            )
            buckets.setdefault(bucket_time, []).append(record)

        return [
            self._summarize_bucket(bucket_time, bucket_records)
            for bucket_time, bucket_records in sorted(buckets.items())
        ]

    def _summarize_bucket(self, bucket_time: datetime, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        detected_records = [
            record for record in records if (record.get("payload") or {}).get("detected")
        ]
        active_records = detected_records or records
        zone = self._most_common_zone(active_records)
        still_time = max(int((record.get("payload") or {}).get("still_time") or 0) for record in records)
        status = self._highest_severity_status(records)
        anomaly = self._combine_detection(records, "anomaly")
        fall_detection = self._combine_detection(records, "fall_detection")

        return {
            **records[-1],
            "timestamp": bucket_time.isoformat(),
            "raw_record_count": len(records),
            "payload": {
                **(records[-1].get("payload") or {}),
                "detected": bool(detected_records),
                "zone": zone,
                "still_time": still_time,
            },
            "status": status,
            "anomaly": anomaly,
            "fall_detection": fall_detection,
        }

    def _most_common_zone(self, records: List[Dict[str, Any]]) -> str:
        counts: Dict[str, int] = {}
        for record in records:
            zone = (record.get("payload") or {}).get("zone") or "unknown"
            counts[zone] = counts.get(zone, 0) + 1
        return max(counts.items(), key=lambda item: item[1])[0] if counts else "unknown"

    def _highest_severity_status(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        statuses = [record.get("status") or {} for record in records]
        if not statuses:
            return {}
        return max(
            statuses,
            key=lambda status: self.STATE_SEVERITY.get(status.get("current_state"), -1),
        )

    def _combine_detection(self, records: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        detections = [record.get(field) or {} for record in records]
        detected = any(bool(detection.get("detected")) for detection in detections)
        selected = next((detection for detection in reversed(detections) if detection.get("detected")), None)
        if selected:
            return selected
        return {**(detections[-1] if detections else {}), "detected": detected}

    def _should_emit_event(
        self,
        event_type: str,
        timestamp: datetime,
        last_event_at: Dict[str, datetime],
    ) -> bool:
        previous = last_event_at.get(event_type)
        if previous and (timestamp - previous).total_seconds() < self.EVENT_COOLDOWN_SECONDS:
            return False
        last_event_at[event_type] = timestamp
        return True

    def _event_summary(
        self,
        *,
        timestamp: Optional[str],
        event_type: str,
        level: str,
        zone: str,
        still_time: int,
        reason: Optional[str],
    ) -> Dict[str, Any]:
        return {
            "timestamp": timestamp,
            "type": event_type,
            "level": level,
            "zone": zone,
            "still_time_seconds": still_time,
            "reason": reason,
        }

    def _is_in_period(self, timestamp: Optional[str], start: datetime, end: datetime) -> bool:
        parsed = self._parse_timestamp(timestamp)
        return parsed is not None and start <= parsed <= end

    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        if not timestamp:
            return None
        try:
            return datetime.fromisoformat(timestamp.replace("Z", ""))
        except ValueError:
            return None


report_service = ReportService()
