from pydantic import BaseModel, Field


class AnalyzeOptions(BaseModel):
    mask: bool = Field(default=True, description="Mask detected secrets and sensitive values.")
    block_high_risk: bool = Field(default=True, description="Recommend blocking high-risk content.")
    log_analysis: bool = Field(default=True, description="Enable line-by-line log anomaly analysis.")


class AnalyzeRequest(BaseModel):
    input_type: str = Field(..., pattern="^(text|file|sql|chat|log)$")
    content: str = Field(..., min_length=1)
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)
