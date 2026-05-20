from app.models.sensor import MmWaveSensorRequest
from app.services.feature_service import feature_service


def test_build_mmwave_feature_vector_maps_sensor_fields():
    feature_vector = feature_service.build_mmwave_feature_vector(
        MmWaveSensorRequest(
            detected=True,
            motion_level=0.7,
            still_time=12,
            zone="toilet",
        )
    )

    assert feature_vector.detected == 1.0
    assert feature_vector.motion_level == 0.7
    assert feature_vector.still_time == 12.0
    assert feature_vector.zone_score == 0.8
    assert feature_vector.is_toilet_zone == 1.0
    assert feature_vector.is_door_zone == 0.0


def test_build_mmwave_feature_vector_uses_defaults():
    feature_vector = feature_service.build_mmwave_feature_vector(
        MmWaveSensorRequest(detected=False)
    )

    assert feature_vector.detected == 0.0
    assert feature_vector.motion_level == 0.0
    assert feature_vector.still_time == 0.0
    assert feature_vector.zone_score == 0.0
    assert feature_vector.distance_from_origin == 0.0
