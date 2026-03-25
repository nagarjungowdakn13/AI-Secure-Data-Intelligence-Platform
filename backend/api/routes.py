from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from backend.models.request_model import AnalyzeOptions, AnalyzeRequest
from backend.models.response_model import AnalyzeResponse, BatchAnalyzeResponse
from backend.services.ai_service import AIService
from backend.services.analysis_pipeline import AnalysisPipeline
from backend.services.correlation_service import CorrelationService
from backend.services.extraction_service import ExtractionService
from backend.services.log_analyzer import LogAnalyzer
from backend.services.masking_service import MaskingService
from backend.services.policy_engine import PolicyEngine
from backend.services.rate_limiter import UploadRateLimiter
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
correlation_service = CorrelationService()
rate_limiter = UploadRateLimiter()
pipeline = AnalysisPipeline(
    regex_detector=regex_detector,
    log_analyzer=log_analyzer,
    risk_engine=risk_engine,
    masking_service=masking_service,
    policy_engine=policy_engine,
    ai_service=ai_service,
    correlation_service=correlation_service,
)


def _client_id(request: Request) -> str:
    return request.client.host if request.client else "unknown-client"


def _read_uploads_with_limits(request: Request, files: List[UploadFile]) -> list[tuple[UploadFile, bytes]]:
    if len(files) > 5:
        raise HTTPException(status_code=413, detail="Too many files uploaded in a single request.")

    payloads: list[tuple[UploadFile, bytes]] = []
    total_bytes = 0
    for file in files:
        data = file.file.read()
        total_bytes += len(data)
        payloads.append((file, data))

    rate_limiter.check(_client_id(request), total_bytes)
    return payloads


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_payload(request: AnalyzeRequest) -> AnalyzeResponse:
    if len(request.content.encode("utf-8")) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Inline payload exceeds the supported size.")

    return pipeline.analyze(
        content=request.content,
        input_type=request.input_type,
        source_name="inline-input",
        options=request.options,
    )


@router.post("/analyze/stream")
async def analyze_stream(request: AnalyzeRequest) -> StreamingResponse:
    if request.input_type not in {"log", "text", "chat", "sql"}:
        raise HTTPException(status_code=400, detail="Streaming analysis currently supports inline text-like inputs only.")

    event_stream = pipeline.stream_events(
        content=request.content,
        input_type=request.input_type,
        source_name="stream-input",
        options=request.options,
    )
    return StreamingResponse(event_stream, media_type="text/event-stream")


@router.post("/analyze/files", response_model=List[AnalyzeResponse])
async def analyze_files(
    request: Request,
    files: List[UploadFile] = File(...),
    mask: bool = Form(True),
    block_high_risk: bool = Form(True),
    log_analysis: bool = Form(True),
) -> List[AnalyzeResponse]:
    options = AnalyzeOptions(mask=mask, block_high_risk=block_high_risk, log_analysis=log_analysis)
    responses: List[AnalyzeResponse] = []

    for file, data in _read_uploads_with_limits(request, files):
        suffix = Path(file.filename or "").suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(data)
            temp_path = Path(temp_file.name)

        try:
            try:
                extracted_content, normalized_type = extraction_service.extract(temp_path, file.filename or temp_path.name)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            responses.append(
                pipeline.analyze(
                    content=extracted_content,
                    input_type=normalized_type,
                    source_name=file.filename or temp_path.name,
                    options=options,
                )
            )
        finally:
            temp_path.unlink(missing_ok=True)

    return responses


@router.post("/analyze/files/correlate", response_model=BatchAnalyzeResponse)
async def analyze_files_with_correlation(
    request: Request,
    files: List[UploadFile] = File(...),
    mask: bool = Form(True),
    block_high_risk: bool = Form(True),
    log_analysis: bool = Form(True),
) -> BatchAnalyzeResponse:
    options = AnalyzeOptions(mask=mask, block_high_risk=block_high_risk, log_analysis=log_analysis)
    responses: List[AnalyzeResponse] = []

    for file, data in _read_uploads_with_limits(request, files):
        suffix = Path(file.filename or "").suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(data)
            temp_path = Path(temp_file.name)

        try:
            try:
                extracted_content, normalized_type = extraction_service.extract(temp_path, file.filename or temp_path.name)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            responses.append(
                pipeline.analyze(
                    content=extracted_content,
                    input_type=normalized_type,
                    source_name=file.filename or temp_path.name,
                    options=options,
                )
            )
        finally:
            temp_path.unlink(missing_ok=True)

    return pipeline.summarize_batch(responses)
