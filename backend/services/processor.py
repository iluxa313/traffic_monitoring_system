from typing import List
from datetime import datetime
from backend.models.domain import RawFlow, ProcessedEvent
from backend.repositories.interfaces import IRawFlowRepository, IProcessedEventRepository
import logging

logger = logging.getLogger(__name__)

class Processor:
    def __init__(self, id: str, raw_repo: IRawFlowRepository, processed_repo: IProcessedEventRepository):
        self.id = id
        self.raw_repo = raw_repo
        self.processed_repo = processed_repo

    def normalize(self, flow: RawFlow) -> RawFlow:
        """Нормализация данных о потоке"""
        # Базовая нормализация - может быть расширена
        flow.srcIP = flow.srcIP.strip()
        flow.dstIP = flow.dstIP.strip()
        flow.protocol = flow.protocol.upper()
        return flow

    def aggregate(self, flow: RawFlow) -> ProcessedEvent:
        """Агрегирование исходного потока в обработанное событие"""
        direction = "INBOUND" if self._is_internal_ip(flow.dstIP) else "OUTBOUND"

        # Извлечь флаги TCP, если применимо
        flags = self._extract_flags(flow)

        return ProcessedEvent(
            flowId=flow.id or 0,
            timestamp=flow.timestamp,
            srcIP=flow.srcIP,
            dstIP=flow.dstIP,
            bytes=flow.sizeBytes,
            flags=flags,
            direction=direction
        )

    def processBatch(self, flows: List[RawFlow]) -> List[ProcessedEvent]:
        """Обработка пакета потоков"""
        processed = []

        for flow in flows:
            try:
                normalized_flow = self.normalize(flow)
                saved_flow = self.raw_repo.save(normalized_flow)
                event = self.aggregate(saved_flow)
                saved_event = self.processed_repo.save(event)
                processed.append(saved_event)

            except Exception as e:
                logger.error(f"Error processing flow: {e}")

        logger.info(f"Processed {len(processed)} events from {len(flows)} flows")
        return processed

    def _is_internal_ip(self, ip: str) -> bool:
        """Проверьте, является ли IP-адрес внутренним"""
        # Упрощенно - проверка частных диапазонов IP-адресов
        parts = ip.split('.')
        if len(parts) != 4:
            return False

        first_octet = int(parts[0])
        second_octet = int(parts[1])

        # 10.0.0.0/8
        if first_octet == 10:
            return True
        # 172.16.0.0/12
        if first_octet == 172 and 16 <= second_octet <= 31:
            return True
        # 192.168.0.0/16
        if first_octet == 192 and second_octet == 168:
            return True

        return False

    def _extract_flags(self, flow: RawFlow) -> str:
        """Извлечение флагов протокола"""
        # Упрощенный вариант — на продакшене будут извлечены фактические флаги TCP.
        if flow.protocol == "TCP":
            return "SYN,ACK"
        return ""
