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


class CorrelationInsight(BaseModel):
    title: str
    detail: str
    severity: str
    related_lines: List[int] = Field(default_factory=list)
    source_names: List[str] = Field(default_factory=list)


class ProcessingMetadata(BaseModel):
    line_count: int = 0
    chunk_count: int = 0
    chunked: bool = False


class AnalyzeResponse(BaseModel):
    summary: str
    content_type: str
    findings: List[Finding]
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    action: str
    risk_breakdown: RiskBreakdown
    recommendations: List[str]
    correlations: List[CorrelationInsight] = Field(default_factory=list)
    processing: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
    insights: List[Insight]
    masked_content: str
    source_name: str


class BatchAnalyzeResponse(BaseModel):
    results: List[AnalyzeResponse]
    cross_log_insights: List[CorrelationInsight] = Field(default_factory=list)
    total_sources: int = 0
    total_findings: int = 0
