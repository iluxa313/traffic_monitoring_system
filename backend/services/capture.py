from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime
from typing import List
import logging
from backend.models.domain import RawFlow

logger = logging.getLogger(__name__)

class CaptureAgent:
    def __init__(self, agentId: str, host: str, interface: str = "eth0"):
        self.agentId = agentId
        self.host = host
        self.status = "stopped"
        self.interface = interface
        self.capture = PacketCapture(interface)

    def start(self):
        self.status = "running"
        logger.info(f"CaptureAgent {self.agentId} started on {self.host}")
        self.capture.startCapture()

    def stop(self):
        self.status = "stopped"
        logger.info(f"CaptureAgent {self.agentId} stopped")
        self.capture.stopCapture()

class PacketCapture:
    def __init__(self, interfaceName: str):
        self.interfaceName = interfaceName
        self.is_capturing = False

    def captureTraffic(self, count: int = 100) -> List[RawFlow]:
        """Захват сетевых пакетов и преобразование их в формат RawFlow"""
        flows = []

        def packet_callback(packet):
            if IP in packet:
                flow = self._packet_to_flow(packet)
                if flow:
                    flows.append(flow)

        try:
            sniff(iface=self.interfaceName, prn=packet_callback, count=count, timeout=10)
        except Exception as e:
            logger.error(f"Capture error: {e}")

        return flows

    def _packet_to_flow(self, packet) -> RawFlow:
        """Преобразование пакетов в RawFlow"""
        try:
            if IP not in packet:
                return None

            ip_layer = packet[IP]
            protocol = "OTHER"
            src_port = 0
            dst_port = 0

            if TCP in packet:
                protocol = "TCP"
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif UDP in packet:
                protocol = "UDP"
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport

            return RawFlow(
                timestamp=datetime.utcnow(),
                srcIP=ip_layer.src,
                dstIP=ip_layer.dst,
                srcPort=src_port,
                dstPort=dst_port,
                protocol=protocol,
                sizeBytes=len(packet)
            )
        except Exception as e:
            logger.error(f"Error converting packet: {e}")
            return None

    def startCapture(self):
        self.is_capturing = True
        logger.info(f"Started capturing on {self.interfaceName}")

    def stopCapture(self):
        self.is_capturing = False
        logger.info(f"Stopped capturing on {self.interfaceName}")
