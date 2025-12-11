from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging
from backend.models.domain import ProcessedEvent, SecurityEvent, BehavioralProfile, EventStatus
from backend.repositories.interfaces import IBehaviorProfileRepository
from backend.config import settings

logger = logging.getLogger(__name__)

class IEventAnalyzer(ABC):
    @abstractmethod
    def analyze(self, events: List[ProcessedEvent]) -> List[SecurityEvent]:
        pass

class DDoSAnalyzer(IEventAnalyzer):
    """Обнаружение DDoS-атак"""

    def analyze(self, events: List[ProcessedEvent]) -> List[SecurityEvent]:
        security_events = []

        # Подсчет запросов на каждый целевой IP-адрес во временном окне
        ip_counts = defaultdict(int)
        for event in events:
            ip_counts[event.dstIP] += 1

        # Проверка порогового значения
        for ip, count in ip_counts.items():
            if count > settings.DDOS_THRESHOLD:
                security_event = SecurityEvent(
                    category="Attack",
                    type="DDoS",
                    severity=3,
                    description=f"Potential DDoS attack detected: {count} requests to {ip}",
                    srcIP="multiple",
                    dstIP=ip,
                    startTime=datetime.utcnow(),
                    status=EventStatus.DETECTED
                )
                security_events.append(security_event)
                logger.warning(f"DDoS detected: {count} requests to {ip}")

        return security_events

class PortScanAnalyzer(IEventAnalyzer):
    """Обнаружение сканирования портов"""

    def analyze(self, events: List[ProcessedEvent]) -> List[SecurityEvent]:
        security_events = []

        # Отслеживание уникальных портов для каждого исходного IP-адреса
        src_ports = defaultdict(set)
        for event in events:
            src_ports[event.srcIP].add(event.dstIP)

        # Проверка сканирования портов
        for src_ip, targets in src_ports.items():
            if len(targets) > settings.PORT_SCAN_THRESHOLD:
                security_event = SecurityEvent(
                    category="Reconnaissance",
                    type="PortScan",
                    severity=2,
                    description=f"Port scan detected from {src_ip}: {len(targets)} targets",
                    srcIP=src_ip,
                    dstIP="multiple",
                    startTime=datetime.utcnow(),
                    status=EventStatus.DETECTED
                )
                security_events.append(security_event)
                logger.warning(f"Port scan detected from {src_ip}")

        return security_events

class MLBehaviorAnalyzer(IEventAnalyzer):
    """Поведенческий анализ на основе машинного обучения"""

    def __init__(self, repo: IBehaviorProfileRepository):
        self.repo = repo
        self.modelName = "BehaviorAnalyzer"
        self.modelVersion = "1.0"
        self.confidenceThreshold = settings.CONFIDENCE_THRESHOLD

    def analyze(self, events: List[ProcessedEvent]) -> List[SecurityEvent]:
        security_events = []

        # Группировка событий по IP-адресу источника
        ip_events = defaultdict(list)
        for event in events:
            ip_events[event.srcIP].append(event)

        # Анализ поведения каждого IP-адреса
        for ip, ip_event_list in ip_events.items():
            profile = self.repo.getByEntity(ip)

            if profile:
                is_anomaly, confidence = self._check_anomaly(ip_event_list, profile)

                if is_anomaly and confidence >= self.confidenceThreshold:
                    security_event = SecurityEvent(
                        category="Anomaly",
                        type="BehavioralAnomaly",
                        severity=2,
                        description=f"Anomalous behavior from {ip} (confidence: {confidence:.2f})",
                        srcIP=ip,
                        dstIP="various",
                        startTime=datetime.utcnow(),
                        status=EventStatus.DETECTED
                    )
                    security_events.append(security_event)

            # Update profile
            self.updateProfiles(ip_event_list)

        return security_events

    def updateProfiles(self, events: List[ProcessedEvent]):
        """Обновление профилей"""
        if not events:
            return

        # Группировка по сущности
        ip_events = defaultdict(list)
        for event in events:
            ip_events[event.srcIP].append(event)

        for ip, ip_event_list in ip_events.items():
            # Вычисление статистики
            total_bytes = sum(e.bytes for e in ip_event_list)
            avg_bytes = total_bytes / len(ip_event_list)
            unique_dsts = len(set(e.dstIP for e in ip_event_list))

            stats = {
                "total_requests": len(ip_event_list),
                "avg_bytes": avg_bytes,
                "unique_destinations": unique_dsts,
                "last_seen": datetime.utcnow().isoformat()
            }

            profile = BehavioralProfile(
                entityId=ip,
                entityType="IP",
                baselineStats=json.dumps(stats),
                lastUpdated=datetime.utcnow()
            )

            self.repo.save(profile)

    def _check_anomaly(self, events: List[ProcessedEvent], profile: BehavioralProfile) -> tuple:
        """Проверка, не является ли поведение аномальным"""
        try:
            baseline = json.loads(profile.baselineStats)

            # Вычисление статистики
            total_bytes = sum(e.bytes for e in events)
            avg_bytes = total_bytes / len(events) if events else 0
            unique_dsts = len(set(e.dstIP for e in events))

            # Простое обнаружение аномалий
            baseline_avg = baseline.get("avg_bytes", 0)
            baseline_dsts = baseline.get("unique_destinations", 0)

            # Проверка на наличие существенных отклонений
            if baseline_avg > 0:
                bytes_ratio = avg_bytes / baseline_avg
                if bytes_ratio > 3 or bytes_ratio < 0.3:
                    return True, 0.85

            if baseline_dsts > 0:
                dst_ratio = unique_dsts / baseline_dsts
                if dst_ratio > 3:
                    return True, 0.80

            return False, 0.5
        except Exception as e:
            logger.error(f"Error checking anomaly: {e}")
            return False, 0.0

class AnalyzerFactory:
    """Фабрика производства анализаторов"""

    @staticmethod
    def createDefaultAnalyzers(repo: IBehaviorProfileRepository) -> List[IEventAnalyzer]:
        return [
            DDoSAnalyzer(),
            PortScanAnalyzer(),
            MLBehaviorAnalyzer(repo)
        ]
