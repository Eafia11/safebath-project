package com.example.safebath.network

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface SafeBathApiService {
    @GET("health")
    suspend fun getHealth(): ApiResponse<HealthData>

    @GET("status")
    suspend fun getStatus(): ApiResponse<StatusSnapshotDto>

    @POST("calibration/start")
    suspend fun startCalibration(
        @Body request: CalibrationStartRequest
    ): ApiResponse<CalibrationStatusDto>

    @POST("calibration/step")
    suspend fun setCalibrationStep(
        @Body request: CalibrationZoneRequest
    ): ApiResponse<CalibrationStatusDto>

    @POST("calibration/complete")
    suspend fun completeCalibrationZone(
        @Body request: CalibrationZoneRequest
    ): ApiResponse<CalibrationStatusDto>
}
