from enum import Enum


# =========================
# 상태 정의
# =========================
class UserState(str, Enum):
    IDLE = "idle"                 # 미사용 상태
    ACTIVE = "active"             # 일반 활동
    TOILET = "toilet"             # 변기 사용
    SHOWER = "shower"             # 샤워 상태
    ANOMALY = "anomaly"           # 이상 상태


# =========================
# 존(위치) 정의
# =========================
class Zone(str, Enum):
    TOILET = "toilet"
    BATH = "bath"
    SHOWER = "shower"
    SINK = "sink"
    ENTRANCE = "entrance"
    UNKNOWN = "unknown"


# =========================
# 이상행동 타입
# =========================
class AnomalyType(str, Enum):
    FALL = "fall"                     # 낙상
    INACTIVITY = "inactivity"         # 장시간 무반응
    ABNORMAL_PATTERN = "abnormal_pattern"  # AI 이상탐지


# =========================
# 임계값 설정 (MVP용)
# =========================
class Threshold:
    # 낙상 의심 기준
    FALL_ACCELERATION = 80

    # 무반응 시간 (초)
    INACTIVITY_SECONDS = 300  # 5분

    # 세션 이상 체류시간 (초)
    MAX_DURATION = 1800  # 30분

    # AI 관련 기본값
    DEFAULT_MAX_MOVING = 25
    DEFAULT_STATIC = 40


# =========================
# 메시지
# =========================
class Message:
    NORMAL = "정상 이용 패턴입니다."
    ANOMALY = "이상행동이 감지되었습니다."
    FALL = "낙상이 의심됩니다!"
    INACTIVITY = "장시간 움직임이 없습니다."
