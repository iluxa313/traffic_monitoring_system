from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.database.db import get_db, UserDB
from backend.api.schemas import Token, UserLogin, IncidentResponse, SystemStatus, TrafficStats
from backend.repositories.implementations import (
    SecurityEventRepositoryDB, RawFlowRepositoryDB, ProcessedEventRepositoryDB,
    FilteringRuleRepositoryDB, BehavioralProfileRepositoryDB, BlockLogRepositoryDB
)
from backend.services.capture import CaptureAgent, PacketCapture
from backend.services.processor import Processor
from backend.services.analyzer import AnalyzerFactory
from backend.services.correlation import CorrelationEngine
from backend.services.response import ResponseController
from backend.models.domain import FilterCriteria, EventStatus
from backend.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Аутентификация
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Конечная точка входа"""
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/status", response_model=SystemStatus)
async def get_status(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Получить состояние системы"""
    event_repo = SecurityEventRepositoryDB(db)

    # Получение информации об активных инцидентах
    criteria = FilterCriteria(
        timeFrom=datetime.utcnow() - timedelta(hours=24)
    )
    events = event_repo.findByCriteria(criteria)

    active = [e for e in events if e.status in [EventStatus.DETECTED, EventStatus.INVESTIGATING]]
    critical = [e for e in events if e.severity >= 3]

    # Расчет сетевой нагрузки (упрощенный вариант)
    raw_repo = RawFlowRepositoryDB(db)
    flows = raw_repo.findByCriteria(criteria)
    total_bytes = sum(f.sizeBytes for f in flows)
    network_load = min(100, (total_bytes / 1000000000) * 100)  # Преобразование в %

    return SystemStatus(
        active_incidents=len(active),
        critical_events=len(critical),
        network_load=network_load,
        status="operational"
    )

@router.get("/incidents", response_model=List[IncidentResponse])
async def get_incidents(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Получение информацию об инцидентах безопасности"""
    event_repo = SecurityEventRepositoryDB(db)

    criteria = FilterCriteria(
        timeFrom=datetime.utcnow() - timedelta(days=7)
    )
    events = event_repo.findByCriteria(criteria)

    return [
        IncidentResponse(
            id=e.id,
            type=e.type,
            severity=e.severity,
            srcIP=e.srcIP,
            dstIP=e.dstIP,
            status=e.status.value,
            time=e.startTime,
            description=e.description
        )
        for e in events
    ]

@router.post("/incidents/{incident_id}/close")
async def close_incident(incident_id: int, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Опасный инцидент"""
    event_repo = SecurityEventRepositoryDB(db)
    success = event_repo.updateStatus(incident_id, EventStatus.CLOSED.value)

    if not success:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"status": "closed"}

@router.get("/traffic/top", response_model=List[TrafficStats])
async def get_top_traffic(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Получение доступа к лучшим источникам трафика"""
    raw_repo = RawFlowRepositoryDB(db)

    criteria = FilterCriteria(
        timeFrom=datetime.utcnow() - timedelta(hours=1)
    )
    flows = raw_repo.findByCriteria(criteria)

    # Агрегирование по источнику
    traffic_by_src = {}
    for flow in flows:
        key = (flow.srcIP, flow.dstIP)
        if key not in traffic_by_src:
            traffic_by_src[key] = 0
        traffic_by_src[key] += flow.sizeBytes

    # Сортировка и получение топ-10
    top_traffic = sorted(traffic_by_src.items(), key=lambda x: x[1], reverse=True)[:10]

    return [
        TrafficStats(srcIP=src, dstIP=dst, bytes=bytes_count)
        for (src, dst), bytes_count in top_traffic
    ]

@router.post("/capture/start")
async def start_capture(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Захват трафика"""
    try:
        # Инициализация репозиториев
        raw_repo = RawFlowRepositoryDB(db)
        processed_repo = ProcessedEventRepositoryDB(db)
        event_repo = SecurityEventRepositoryDB(db)
        profile_repo = BehavioralProfileRepositoryDB(db)

        agent = CaptureAgent("agent-1", "localhost", settings.CAPTURE_INTERFACE)
        flows = agent.capture.captureTraffic(count=50)

        processor = Processor("proc-1", raw_repo, processed_repo)
        events = processor.processBatch(flows)

        analyzers = AnalyzerFactory.createDefaultAnalyzers(profile_repo)
        correlation_engine = CorrelationEngine("corr-1", profile_repo)
        correlation_engine.setAnalyzers(analyzers)
        security_events = correlation_engine.analyze(events)

        # Сохранение событий безопасности
        for se in security_events:
            event_repo.saveEvent(se)

        return {
            "captured": len(flows),
            "processed": len(events),
            "incidents": len(security_events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules")
async def get_rules(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Получение правила фильтрации"""
    rule_repo = FilteringRuleRepositoryDB(db)
    rules = rule_repo.findActive()
    return rules

@router.post("/rules")
async def create_rule(rule: dict, db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Создание правила фильтрации"""
    from backend.models.domain import FilteringRule

    rule_repo = FilteringRuleRepositoryDB(db)
    new_rule = FilteringRule(**rule)
    saved_rule = rule_repo.add(new_rule)

    return saved_rule
