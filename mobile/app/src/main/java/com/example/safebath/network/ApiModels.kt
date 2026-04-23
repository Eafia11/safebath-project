package com.example.safebath.network

data class ApiResponse<T>(
    val success: Boolean,
    val message: String,
    val data: T?
)

data class HealthData(
    val status: String
)

data class StatusSnapshotDto(
    val current_state: String,
    val last_door_state: String?,
    val last_mmwave_detected: Boolean,
    val last_zone: String?,
    val last_motion_level: Float?,
    val last_still_time: Int?,
    val last_reason: String,
    val last_updated: String?,
    val waiting_for_response: Boolean,
    val abnormal_start_time: String?
)

data class CalibrationStartRequest(
    val user_id: String
)

data class CalibrationZoneRequest(
    val zone_name: String,
    val center_x: Float? = null,
    val center_y: Float? = null,
    val radius: Float? = null,
)

data class CalibrationStatusDto(
    val is_active: Boolean,
    val user_id: String?,
    val current_step: String?,
    val started_at: String?,
    val completed_zones: List<String>,
    val progress: String
)
