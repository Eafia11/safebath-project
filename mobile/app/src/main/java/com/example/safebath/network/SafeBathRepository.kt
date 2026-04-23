package com.example.safebath.network

class SafeBathRepository(
    private val api: SafeBathApiService = NetworkModule.apiService
) {
    suspend fun checkHealth(): ApiResponse<HealthData> = api.getHealth()

    suspend fun getStatus(): ApiResponse<StatusSnapshotDto> = api.getStatus()

    suspend fun startCalibration(userId: String): ApiResponse<CalibrationStatusDto> {
        return api.startCalibration(CalibrationStartRequest(user_id = userId))
    }

    suspend fun setCalibrationStep(zoneName: String): ApiResponse<CalibrationStatusDto> {
        return api.setCalibrationStep(CalibrationZoneRequest(zone_name = zoneName))
    }

    suspend fun completeCalibration(
        zoneName: String,
        centerX: Float,
        centerY: Float,
        radius: Float,
    ): ApiResponse<CalibrationStatusDto> {
        return api.completeCalibrationZone(
            CalibrationZoneRequest(
                zone_name = zoneName,
                center_x = centerX,
                center_y = centerY,
                radius = radius,
            )
        )
    }
}
