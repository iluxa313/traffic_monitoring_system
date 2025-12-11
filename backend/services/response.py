from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
import logging
from backend.models.domain import SecurityEvent, FilteringRule, BlockLogEntry
from backend.repositories.interfaces import IFilteringRuleRepository, IBlockLogRepository
from backend.config import settings

logger = logging.getLogger(__name__)

class ICountermeasureStrategy(ABC):
    @abstractmethod
    def apply(self, event: SecurityEvent):
        pass

class ManualBlockStrategy(ICountermeasureStrategy):
    """Стратегия ручной блокировки"""

    def __init__(self, rule_repo: IFilteringRuleRepository, log_repo: IBlockLogRepository):
        self.rule_repo = rule_repo
        self.log_repo = log_repo

    def apply(self, event: SecurityEvent):
        logger.info(f"Manual block requested for event {event.id}")
        # На продакшене это потребовало бы одобрения человека
        # Пока что просто лог
        return

class AutoBlockStrategy(ICountermeasureStrategy):
    """Automatic blocking strategy"""

    def __init__(self, rule_repo: IFilteringRuleRepository, log_repo: IBlockLogRepository):
        self.rule_repo = rule_repo
        self.log_repo = log_repo
        self.temporaryBlockDurationMin = settings.TEMPORARY_BLOCK_DURATION

    def apply(self, event: SecurityEvent):
        """Применить автоматические контрмеры"""
        # Создание временного правило блокировки
        rule = self.createTemporaryRule(event)

        if rule:
            saved_rule = self.rule_repo.add(rule)

            log_entry = BlockLogEntry(
                time=datetime.utcnow(),
                ruleId=saved_rule.id,
                eventId=event.id or 0,
                action="auto",
                initiator="AutoBlockStrategy"
            )
            self.log_repo.addEntry(log_entry)

            logger.info(f"Auto-blocked {event.srcIP} for event {event.id}")

    def createTemporaryRule(self, event: SecurityEvent) -> FilteringRule:
        """Создание временного правила фильтрации"""
        expiration = datetime.utcnow() + timedelta(minutes=self.temporaryBlockDurationMin)

        return FilteringRule(
            name=f"AutoBlock-{event.type}-{event.srcIP}",
            category=event.category,
            type=event.type,
            severity=event.severity,
            srcIP=event.srcIP,
            dstIP=event.dstIP,
            action="DROP",
            expiration=expiration
        )

class ResponseController:
    """Управление реагированием на события безопасности"""

    def __init__(self, rule_repo: IFilteringRuleRepository, log_repo: IBlockLogRepository):
        self.strategies: List[ICountermeasureStrategy] = []
        self.rule_repo = rule_repo
        self.log_repo = log_repo

    def registerStrategy(self, strategy: ICountermeasureStrategy):
        self.strategies.append(strategy)
        logger.info(f"Registered strategy: {strategy.__class__.__name__}")

    def applyCountermeasure(self, event: SecurityEvent):
        """Применение контрмеры при инциденте безопасности"""
        # Автоматическая блокировка событий высокой степени серьезности
        if event.severity >= 3:
            auto_strategy = AutoBlockStrategy(self.rule_repo, self.log_repo)
            auto_strategy.apply(event)
        else:
            # Лог для ручной проверки
            logger.info(f"Event {event.id} requires manual review (severity: {event.severity})")

class SecuritySpecialist:
    """Действия специалиста по безопасности"""

    def __init__(self, response_controller: ResponseController, log_repo: IBlockLogRepository):
        self.response_controller = response_controller
        self.log_repo = log_repo

    def analyzeEvent(self, event: SecurityEvent):
        logger.info(f"Security specialist analyzing event {event.id}")

    def requestManualBlock(self, event: SecurityEvent):
        """Запрос на ручную блокировку"""
        manual_strategy = ManualBlockStrategy(
            self.response_controller.rule_repo,
            self.log_repo
        )
        manual_strategy.apply(event)

    def viewBlockHistory(self, eventId: int) -> List[BlockLogEntry]:
        """Просмотр истории блокировок для события"""
        return self.log_repo.findByEvent(eventId)
