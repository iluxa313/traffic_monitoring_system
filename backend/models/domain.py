from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

class EventStatus(str, Enum):
    DETECTED = "Detected"
    INVESTIGATING = "Investigating"
    MITIGATED = "Mitigated"
    CLOSED = "Closed"

class RawFlow(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    srcIP: str
    dstIP: str
    srcPort: int
    dstPort: int
    protocol: str
    sizeBytes: int

    class Config:
        from_attributes = True

class ProcessedEvent(BaseModel):
    id: Optional[int] = None
    flowId: int
    timestamp: datetime
    srcIP: str
    dstIP: str
    bytes: int
    flags: str
    direction: str

    class Config:
        from_attributes = True

class SecurityEvent(BaseModel):
    id: Optional[int] = None
    category: str
    type: str
    severity: int
    description: str
    srcIP: str
    dstIP: str
    startTime: datetime
    endTime: Optional[datetime] = None
    status: EventStatus = EventStatus.DETECTED

    class Config:
        from_attributes = True

class FilterCriteria(BaseModel):
    timeFrom: Optional[datetime] = None
    timeTo: Optional[datetime] = None
    srcIP: Optional[str] = None
    dstIP: Optional[str] = None
    protocol: Optional[str] = None
    minSeverity: Optional[int] = None

class BehavioralProfile(BaseModel):
    id: Optional[int] = None
    entityId: str
    entityType: str  # IP, subnet, service
    baselineStats: str  # JSON string with stats
    lastUpdated: datetime

    class Config:
        from_attributes = True

class FilteringRule(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    type: str
    severity: int
    srcIP: Optional[str] = None
    dstIP: Optional[str] = None
    action: str  # DROP, REJECT, ACCEPT
    expiration: Optional[datetime] = None

    class Config:
        from_attributes = True

class BlockLogEntry(BaseModel):
    id: Optional[int] = None
    time: datetime
    ruleId: int
    eventId: int
    action: str  # auto, manual
    initiator: str

    class Config:
        from_attributes = True
