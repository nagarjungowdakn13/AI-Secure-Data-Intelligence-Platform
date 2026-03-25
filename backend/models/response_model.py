from typing import List, Optional

from pydantic import BaseModel, Field


class Finding(BaseModel):
    category: str
    label: str
    severity: str
    line_number: Optional[int] = None
    matched_text: str
    masked_text: str
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    explanation: str
    source_name: Optional[str] = None


class Insight(BaseModel):
    title: str
    detail: str


class RiskBreakdown(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class AnalyzeResponse(BaseModel):
    summary: str
    content_type: str
    findings: List[Finding]
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    action: str
    risk_breakdown: RiskBreakdown
    recommendations: List[str]
    insights: List[Insight]
    masked_content: str
    source_name: str
