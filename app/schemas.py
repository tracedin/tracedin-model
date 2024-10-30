from pydantic import BaseModel
from typing import List

class Span(BaseModel):
    traceId: str
    projectKey: str
    id: str
    duration: int

class AnomalyTraceResult(BaseModel):
    isAnomaly: bool
    traceId: str
    projectKey: str
    spanIds: List[str]