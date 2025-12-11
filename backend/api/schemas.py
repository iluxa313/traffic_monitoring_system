from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class IncidentResponse(BaseModel):
    id: int
    type: str
    severity: int
    srcIP: str
    dstIP: str
    status: str
    time: datetime
    description: str

class TrafficStats(BaseModel):
    srcIP: str
    dstIP: str
    bytes: int

class SystemStatus(BaseModel):
    active_incidents: int
    critical_events: int
    network_load: float
    status: str
