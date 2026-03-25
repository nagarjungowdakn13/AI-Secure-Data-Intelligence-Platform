from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.models.request_model import AnalyzeOptions, AnalyzeRequest
from backend.models.response_model import AnalyzeResponse
from backend.services.ai_service import AIService
from backend.services.extraction_service import ExtractionService
from backend.services.log_analyzer import LogAnalyzer
from backend.services.masking_service import MaskingService
from backend.services.policy_engine import PolicyEngine
from backend.services.regex_detector import RegexDetector
from backend.services.risk_engine import RiskEngine


router = APIRouter(tags=["analysis"])

regex_detector = RegexDetector()
masking_service = MaskingService()
log_analyzer = LogAnalyzer()
risk_engine = RiskEngine()
policy_engine = PolicyEngine()
extraction_service = ExtractionService()
ai_service = AIService()


def _run_analysis(*, content: str, input_type: str, source_name: str, options: AnalyzeOptions) -> AnalyzeResponse:
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="No analyzable content provided.")

    findings = regex_detector.scan_content(content, source_name=source_name)
    log_findings = log_analyzer.analyze(content, source_name=source_name) if options.log_analysis else []
    merged_findings = risk_engine.merge_findings(findings + log_findings)

    risk_assessment = risk_engine.score(merged_findings)
    masked_content = masking_service.mask_content(content, merged_findings) if options.mask else content
    action = policy_engine.determine_action(
        risk_level=risk_assessment["risk_level"],
        block_high_risk=options.block_high_risk,
    )
    insights = ai_service.generate_insights(
        content=masked_content,
        findings=merged_findings,
        risk_assessment=risk_assessment,
        input_type=input_type,
    )

    return AnalyzeResponse(
        summary=insights["summary"],
        content_type=input_type,
        findings=merged_findings,
        risk_score=risk_assessment["risk_score"],
        risk_level=risk_assessment["risk_level"],
        action=action,
        risk_breakdown=risk_assessment["risk_breakdown"],
        recommendations=risk_assessment["recommendations"],
        insights=insights["insights"],
        masked_content=masked_content,
        source_name=source_name,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_payload(request: AnalyzeRequest) -> AnalyzeResponse:
    return _run_analysis(
        content=request.content,
        input_type=request.input_type,
        source_name="inline-input",
        options=request.options,
    )


@router.post("/analyze/files", response_model=List[AnalyzeResponse])
async def analyze_files(
    files: List[UploadFile] = File(...),
    mask: bool = Form(True),
    block_high_risk: bool = Form(True),
    log_analysis: bool = Form(True),
) -> List[AnalyzeResponse]:
    options = AnalyzeOptions(mask=mask, block_high_risk=block_high_risk, log_analysis=log_analysis)
    responses: List[AnalyzeResponse] = []

    for file in files:
        suffix = Path(file.filename or "").suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await file.read())
            temp_path = Path(temp_file.name)

        try:
            try:
                extracted_content, normalized_type = extraction_service.extract(temp_path, file.filename or temp_path.name)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            responses.append(
                _run_analysis(
                    content=extracted_content,
                    input_type=normalized_type,
                    source_name=file.filename or temp_path.name,
                    options=options,
                )
            )
        finally:
            temp_path.unlink(missing_ok=True)

    return responses
