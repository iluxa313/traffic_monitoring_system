from typing import List
import logging
from backend.models.domain import ProcessedEvent, SecurityEvent
from backend.services.analyzer import IEventAnalyzer, AnalyzerFactory
from backend.repositories.interfaces import IBehaviorProfileRepository

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """Сопоставление событий и выявление инцидентов безопасности"""

    def __init__(self, engineId: str, profile_repo: IBehaviorProfileRepository):
        self.engineId = engineId
        self.thresholdsProfile = "default"
        self.analyzers: List[IEventAnalyzer] = []
        self.profile_repo = profile_repo

    def setAnalyzers(self, analyzers: List[IEventAnalyzer]):
        self.analyzers = analyzers
        logger.info(f"CorrelationEngine {self.engineId}: Set {len(analyzers)} analyzers")

    def analyze(self, events: List[ProcessedEvent]) -> List[SecurityEvent]:
        """Анализ событий, используя все настроенные анализаторы"""
        all_security_events = []

        for analyzer in self.analyzers:
            try:
                security_events = analyzer.analyze(events)
                all_security_events.extend(security_events)
                logger.info(f"{analyzer.__class__.__name__} found {len(security_events)} events")
            except Exception as e:
                logger.error(f"Analyzer {analyzer.__class__.__name__} error: {e}")

        return all_security_events
