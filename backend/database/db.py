from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import settings

Base = declarative_base()

class RawFlowDB(Base):
    __tablename__ = "raw_flows"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    srcIP = Column(String(45))
    dstIP = Column(String(45))
    srcPort = Column(Integer)
    dstPort = Column(Integer)
    protocol = Column(String(10))
    sizeBytes = Column(Integer)

class ProcessedEventDB(Base):
    __tablename__ = "processed_events"

    id = Column(Integer, primary_key=True, index=True)
    flowId = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    srcIP = Column(String(45))
    dstIP = Column(String(45))
    bytes = Column(Integer)
    flags = Column(String(50))
    direction = Column(String(20))

class SecurityEventDB(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50))
    type = Column(String(50))
    severity = Column(Integer)
    description = Column(Text)
    srcIP = Column(String(45))
    dstIP = Column(String(45))
    startTime = Column(DateTime, default=datetime.utcnow)
    endTime = Column(DateTime, nullable=True)
    status = Column(String(20))

class BehavioralProfileDB(Base):
    __tablename__ = "behavioral_profiles"

    id = Column(Integer, primary_key=True, index=True)
    entityId = Column(String(100))
    entityType = Column(String(50))
    baselineStats = Column(Text)
    lastUpdated = Column(DateTime, default=datetime.utcnow)

class FilteringRuleDB(Base):
    __tablename__ = "filtering_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    category = Column(String(50))
    type = Column(String(50))
    severity = Column(Integer)
    srcIP = Column(String(45), nullable=True)
    dstIP = Column(String(45), nullable=True)
    action = Column(String(20))
    expiration = Column(DateTime, nullable=True)

class BlockLogEntryDB(Base):
    __tablename__ = "block_log_entries"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime, default=datetime.utcnow)
    ruleId = Column(Integer)
    eventId = Column(Integer)
    action = Column(String(20))
    initiator = Column(String(100))

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100))
    hashed_password = Column(String(100))
    role = Column(String(50))
    is_active = Column(Boolean, default=True)

# Механизм базы данных и сессия
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
