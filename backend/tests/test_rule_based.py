from datetime import datetime, timedelta

from app.detectors.inactivity_detector import InactivityDetector


def test_inactivity_rule_detects_prolonged_still_time():
    detector = InactivityDetector()

    result = detector.evaluate_mmwave_rules(
        detected=True,
        still_time=30,
    )

    assert result["triggered"] is True
    assert result["rule_type"] == "prolonged_inactivity"
    assert result["next_state"] == "ABNORMAL"


def test_rule_detects_occupancy_ended_when_door_is_closed():
    detector = InactivityDetector()

    result = detector.evaluate_mmwave_rules(
        detected=False,
        last_door_state="closed",
    )

    assert result["triggered"] is True
    assert result["rule_type"] == "occupancy_ended"
    assert result["next_state"] == "EMPTY"


def test_response_timeout_rule_triggers_after_timeout():
    detector = InactivityDetector()

    result = detector.evaluate_response_timeout(
        waiting_for_response=True,
        abnormal_start_time=datetime.utcnow() - timedelta(seconds=11),
        timeout_seconds=10,
    )

    assert result["triggered"] is True
    assert result["rule_type"] == "response_timeout"
