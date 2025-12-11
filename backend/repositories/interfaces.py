from abc import ABC, abstractmethod
from typing import List, Optional
from backend.models.domain import (
    RawFlow, ProcessedEvent, SecurityEvent, FilterCriteria,
    BehavioralProfile, FilteringRule, BlockLogEntry
)

class IRawFlowRepository(ABC):
    @abstractmethod
    def save(self, flow: RawFlow) -> RawFlow:
        pass

    @abstractmethod
    def getById(self, id: int) -> Optional[RawFlow]:
        pass

    @abstractmethod
    def findByCriteria(self, criteria: FilterCriteria) -> List[RawFlow]:
        pass

class IProcessedEventRepository(ABC):
    @abstractmethod
    def save(self, event: ProcessedEvent) -> ProcessedEvent:
        pass

    @abstractmethod
    def findByCriteria(self, criteria: FilterCriteria) -> List[ProcessedEvent]:
        pass

class ISecurityEventRepository(ABC):
    @abstractmethod
    def saveEvent(self, event: SecurityEvent) -> SecurityEvent:
        pass

    @abstractmethod
    def findByCriteria(self, criteria: FilterCriteria) -> List[SecurityEvent]:
        pass

    @abstractmethod
    def getById(self, id: int) -> Optional[SecurityEvent]:
        pass

    @abstractmethod
    def updateStatus(self, id: int, status: str) -> bool:
        pass

class IBehaviorProfileRepository(ABC):
    @abstractmethod
    def getByEntity(self, entityId: str) -> Optional[BehavioralProfile]:
        pass

    @abstractmethod
    def save(self, profile: BehavioralProfile) -> BehavioralProfile:
        pass

    @abstractmethod
    def listAbnormalProfiles(self) -> List[BehavioralProfile]:
        pass

class IFilteringRuleRepository(ABC):
    @abstractmethod
    def add(self, rule: FilteringRule) -> FilteringRule:
        pass

    @abstractmethod
    def remove(self, id: int) -> bool:
        pass

    @abstractmethod
    def findActive(self) -> List[FilteringRule]:
        pass

class IBlockLogRepository(ABC):
    @abstractmethod
    def addEntry(self, entry: BlockLogEntry) -> BlockLogEntry:
        pass

    @abstractmethod
    def findByEvent(self, eventId: int) -> List[BlockLogEntry]:
        pass
