import os
from typing import Optional

class Settings:
    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/traffic_monitor")

    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Захват трафика
    CAPTURE_INTERFACE: str = os.getenv("CAPTURE_INTERFACE", "eth0")
    DDOS_THRESHOLD: int = 10000  # запросов в секунду
    PORT_SCAN_THRESHOLD: int = 100  # порты во временном окне
    TEMPORARY_BLOCK_DURATION: int = 30  # минуты

    # Настройки машинного обучения
    ML_MODEL_PATH: str = "models/behavior_analyzer.pkl"
    CONFIDENCE_THRESHOLD: float = 0.75
    CORRELATION_THRESHOLD: float = 0.8

    # Система
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

settings = Settings()
