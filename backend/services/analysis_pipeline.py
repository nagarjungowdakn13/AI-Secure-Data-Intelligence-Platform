from __future__ import annotations

import json
import math
import os
from typing import Iterable

from backend.models.response_model import AnalyzeResponse, BatchAnalyzeResponse


class AnalysisPipeline:
    def __init__(self, *, regex_detector, log_analyzer, risk_engine, masking_service, policy_engine, ai_service, correlation_service) -> None:
        self.regex_detector = regex_detector
        self.log_analyzer = log_analyzer
        self.risk_engine = risk_engine
        self.masking_service = masking_service
        self.policy_engine = policy_engine
        self.ai_service = ai_service
        self.correlation_service = correlation_service
        self.chunk_lines = int(os.getenv("ANALYSIS_CHUNK_LINES", "200"))

    def analyze(self, *, content: str, input_type: str, source_name: str, options) -> AnalyzeResponse:
        collected_findings, processing = self._collect_findings(content, source_name, options)
        merged_findings = self.risk_engine.merge_findings(collected_findings)
        correlations = self.correlation_service.summarize(merged_findings, source_name)
        risk_assessment = self.risk_engine.score(merged_findings)
        masked_content = self.masking_service.mask_content(content, merged_findings) if options.mask else content
        action = self.policy_engine.determine_action(
            risk_level=risk_assessment["risk_level"],
            block_high_risk=options.block_high_risk,
        )
        insights = self.ai_service.generate_insights(
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
            correlations=correlations,
            processing=processing,
            insights=insights["insights"],
            masked_content=masked_content,
            source_name=source_name,
        )

    def stream_events(self, *, content: str, input_type: str, source_name: str, options) -> Iterable[str]:
        lines = content.splitlines()
        total_chunks = max(1, math.ceil(max(len(lines), 1) / self.chunk_lines))

        if not lines:
            lines = [content]

        for chunk_index, start in enumerate(range(0, len(lines), self.chunk_lines), start=1):
            chunk_lines = lines[start : start + self.chunk_lines]
            chunk_text = "\n".join(chunk_lines)
            line_start = start + 1
            line_end = start + len(chunk_lines)

            chunk_findings = self.regex_detector.scan_content(chunk_text, source_name=source_name, start_line=line_start)
            if options.log_analysis:
                chunk_findings.extend(self.log_analyzer.analyze(chunk_text, source_name=source_name, start_line=line_start))
            merged_chunk = self.risk_engine.merge_findings(chunk_findings)
            chunk_risk = self.risk_engine.score(merged_chunk)
            payload = {
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "line_start": line_start,
                "line_end": line_end,
                "findings_count": len(merged_chunk),
                "risk_level": chunk_risk["risk_level"],
                "labels": sorted({finding["label"] for finding in merged_chunk}),
            }
            yield f"event: chunk\ndata: {json.dumps(payload)}\n\n"

        final_result = self.analyze(content=content, input_type=input_type, source_name=source_name, options=options)
        yield f"event: complete\ndata: {json.dumps(final_result.model_dump())}\n\n"

    def summarize_batch(self, results: list[AnalyzeResponse]) -> BatchAnalyzeResponse:
        cross_log_insights = self.correlation_service.summarize_across_sources(results)
        return BatchAnalyzeResponse(
            results=results,
            cross_log_insights=cross_log_insights,
            total_sources=len(results),
            total_findings=sum(len(result.findings) for result in results),
        )

    def _collect_findings(self, content: str, source_name: str, options) -> tuple[list[dict], dict]:
        lines = content.splitlines()
        if not lines:
            lines = [content]

        collected_findings: list[dict] = []
        chunk_count = 0
        for start in range(0, len(lines), self.chunk_lines):
            chunk_lines = lines[start : start + self.chunk_lines]
            chunk_text = "\n".join(chunk_lines)
            start_line = start + 1
            collected_findings.extend(self.regex_detector.scan_content(chunk_text, source_name=source_name, start_line=start_line))
            if options.log_analysis:
                collected_findings.extend(self.log_analyzer.analyze(chunk_text, source_name=source_name, start_line=start_line))
            chunk_count += 1

        processing = {
            "line_count": len(lines),
            "chunk_count": chunk_count,
            "chunked": chunk_count > 1,
        }
        return collected_findings, processing
