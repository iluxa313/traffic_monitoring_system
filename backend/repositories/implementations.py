from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.repositories.interfaces import (
    IRawFlowRepository, IProcessedEventRepository, ISecurityEventRepository,
    IBehaviorProfileRepository, IFilteringRuleRepository, IBlockLogRepository
)
from backend.models.domain import (
    RawFlow, ProcessedEvent, SecurityEvent, FilterCriteria,
    BehavioralProfile, FilteringRule, BlockLogEntry
)
from backend.database.db import (
    RawFlowDB, ProcessedEventDB, SecurityEventDB,
    BehavioralProfileDB, FilteringRuleDB, BlockLogEntryDB
)

class RawFlowRepositoryDB(IRawFlowRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, flow: RawFlow) -> RawFlow:
        db_flow = RawFlowDB(**flow.dict(exclude={'id'}))
        self.db.add(db_flow)
        self.db.commit()
        self.db.refresh(db_flow)
        flow.id = db_flow.id
        return flow

    def getById(self, id: int) -> Optional[RawFlow]:
        db_flow = self.db.query(RawFlowDB).filter(RawFlowDB.id == id).first()
        return RawFlow.from_orm(db_flow) if db_flow else None

    def findByCriteria(self, criteria: FilterCriteria) -> List[RawFlow]:
        query = self.db.query(RawFlowDB)

        if criteria.timeFrom:
            query = query.filter(RawFlowDB.timestamp >= criteria.timeFrom)
        if criteria.timeTo:
            query = query.filter(RawFlowDB.timestamp <= criteria.timeTo)
        if criteria.srcIP:
            query = query.filter(RawFlowDB.srcIP == criteria.srcIP)
        if criteria.dstIP:
            query = query.filter(RawFlowDB.dstIP == criteria.dstIP)
        if criteria.protocol:
            query = query.filter(RawFlowDB.protocol == criteria.protocol)

        return [RawFlow.from_orm(f) for f in query.all()]

class ProcessedEventRepositoryDB(IProcessedEventRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, event: ProcessedEvent) -> ProcessedEvent:
        db_event = ProcessedEventDB(**event.dict(exclude={'id'}))
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        event.id = db_event.id
        return event

    def findByCriteria(self, criteria: FilterCriteria) -> List[ProcessedEvent]:
        query = self.db.query(ProcessedEventDB)

        if criteria.timeFrom:
            query = query.filter(ProcessedEventDB.timestamp >= criteria.timeFrom)
        if criteria.timeTo:
            query = query.filter(ProcessedEventDB.timestamp <= criteria.timeTo)
        if criteria.srcIP:
            query = query.filter(ProcessedEventDB.srcIP == criteria.srcIP)
        if criteria.dstIP:
            query = query.filter(ProcessedEventDB.dstIP == criteria.dstIP)

        return [ProcessedEvent.from_orm(e) for e in query.all()]

class SecurityEventRepositoryDB(ISecurityEventRepository):
    def __init__(self, db: Session):
        self.db = db

    def saveEvent(self, event: SecurityEvent) -> SecurityEvent:
        db_event = SecurityEventDB(**event.dict(exclude={'id'}))
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        event.id = db_event.id
        return event

    def findByCriteria(self, criteria: FilterCriteria) -> List[SecurityEvent]:
        query = self.db.query(SecurityEventDB)

        if criteria.timeFrom:
            query = query.filter(SecurityEventDB.startTime >= criteria.timeFrom)
        if criteria.timeTo:
            query = query.filter(SecurityEventDB.startTime <= criteria.timeTo)
        if criteria.srcIP:
            query = query.filter(SecurityEventDB.srcIP == criteria.srcIP)
        if criteria.dstIP:
            query = query.filter(SecurityEventDB.dstIP == criteria.dstIP)
        if criteria.minSeverity:
            query = query.filter(SecurityEventDB.severity >= criteria.minSeverity)

        return [SecurityEvent.from_orm(e) for e in query.all()]

    def getById(self, id: int) -> Optional[SecurityEvent]:
        db_event = self.db.query(SecurityEventDB).filter(SecurityEventDB.id == id).first()
        return SecurityEvent.from_orm(db_event) if db_event else None

    def updateStatus(self, id: int, status: str) -> bool:
        db_event = self.db.query(SecurityEventDB).filter(SecurityEventDB.id == id).first()
        if db_event:
            db_event.status = status
            self.db.commit()
            return True
        return False

class BehavioralProfileRepositoryDB(IBehaviorProfileRepository):
    def __init__(self, db: Session):
        self.db = db

    def getByEntity(self, entityId: str) -> Optional[BehavioralProfile]:
        db_profile = self.db.query(BehavioralProfileDB).filter(
            BehavioralProfileDB.entityId == entityId
        ).first()
        return BehavioralProfile.from_orm(db_profile) if db_profile else None

    def save(self, profile: BehavioralProfile) -> BehavioralProfile:
        existing = self.db.query(BehavioralProfileDB).filter(
            BehavioralProfileDB.entityId == profile.entityId
        ).first()

        if existing:
            existing.baselineStats = profile.baselineStats
            existing.lastUpdated = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return BehavioralProfile.from_orm(existing)
        else:
            db_profile = BehavioralProfileDB(**profile.dict(exclude={'id'}))
            self.db.add(db_profile)
            self.db.commit()
            self.db.refresh(db_profile)
            profile.id = db_profile.id
            return profile

    def listAbnormalProfiles(self) -> List[BehavioralProfile]:
        # Упрощенный вариант: пока возвращает все профили
        profiles = self.db.query(BehavioralProfileDB).all()
        return [BehavioralProfile.from_orm(p) for p in profiles]

class FilteringRuleRepositoryDB(IFilteringRuleRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, rule: FilteringRule) -> FilteringRule:
        db_rule = FilteringRuleDB(**rule.dict(exclude={'id'}))
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        rule.id = db_rule.id
        return rule

    def remove(self, id: int) -> bool:
        db_rule = self.db.query(FilteringRuleDB).filter(FilteringRuleDB.id == id).first()
        if db_rule:
            self.db.delete(db_rule)
            self.db.commit()
            return True
        return False

    def findActive(self) -> List[FilteringRule]:
        now = datetime.utcnow()
        query = self.db.query(FilteringRuleDB).filter(
            (FilteringRuleDB.expiration.is_(None)) | (FilteringRuleDB.expiration > now)
        )
        return [FilteringRule.from_orm(r) for r in query.all()]

class BlockLogRepositoryDB(IBlockLogRepository):
    def __init__(self, db: Session):
        self.db = db

    def addEntry(self, entry: BlockLogEntry) -> BlockLogEntry:
        db_entry = BlockLogEntryDB(**entry.dict(exclude={'id'}))
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        entry.id = db_entry.id
        return entry

    def findByEvent(self, eventId: int) -> List[BlockLogEntry]:
        entries = self.db.query(BlockLogEntryDB).filter(
            BlockLogEntryDB.eventId == eventId
        ).all()
        return [BlockLogEntry.from_orm(e) for e in entries]
