from __future__ import annotations

from collections import Counter, defaultdict


class CorrelationService:
    def summarize(self, findings: list[dict], source_name: str) -> list[dict]:
        correlations: list[dict] = []
        grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)

        for finding in findings:
            grouped[(finding["label"], finding["matched_text"])].append(finding)

        for (label, matched_text), items in grouped.items():
            if len(items) < 2:
                continue
            correlations.append(
                {
                    "title": f"Repeated {label} across log entries",
                    "detail": f"The value '{self._safe_value(matched_text)}' appears in {len(items)} correlated log entries.",
                    "severity": self._highest_severity(items),
                    "related_lines": [item["line_number"] for item in items if item.get("line_number")],
                    "source_names": [source_name],
                }
            )

        labels = Counter(finding["label"] for finding in findings)
        if labels.get("repeated_failure", 0) >= 3:
            correlations.append(
                {
                    "title": "Repeated authentication failure cluster",
                    "detail": "Multiple failure-related log entries indicate a probable brute-force, abuse, or misconfiguration pattern.",
                    "severity": "high",
                    "related_lines": [finding["line_number"] for finding in findings if finding["label"] == "repeated_failure"],
                    "source_names": [source_name],
                }
            )

        if labels.get("stack_trace", 0) and {"password", "api_key", "token", "secret_key", "client_secret"} & set(labels):
            correlations.append(
                {
                    "title": "Credential exposure with application error context",
                    "detail": "Sensitive credentials and internal error details appear together, increasing exploitation risk.",
                    "severity": "critical",
                    "related_lines": [finding["line_number"] for finding in findings if finding["label"] in {"stack_trace", "password", "api_key", "token", "secret_key", "client_secret"}],
                    "source_names": [source_name],
                }
            )

        return correlations[:6]

    def summarize_across_sources(self, results: list) -> list[dict]:
        grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for result in results:
            for finding in result.findings:
                grouped[(finding.label, finding.matched_text)].append({"source_name": finding.source_name or result.source_name, "line_number": finding.line_number, "severity": finding.severity})

        insights: list[dict] = []
        for (label, matched_text), items in grouped.items():
            sources = sorted({item["source_name"] for item in items if item.get("source_name")})
            if len(sources) < 2:
                continue
            insights.append(
                {
                    "title": f"Cross-log correlation for {label}",
                    "detail": f"The value '{self._safe_value(matched_text)}' appears across {len(sources)} separate log sources.",
                    "severity": self._highest_severity(items),
                    "related_lines": [item["line_number"] for item in items if item.get("line_number")],
                    "source_names": sources,
                }
            )

        if not insights and len(results) > 1:
            suspicious_sources = [result.source_name for result in results if result.risk_level in {"high", "critical"}]
            if len(suspicious_sources) > 1:
                insights.append(
                    {
                        "title": "Multiple high-risk logs detected",
                        "detail": "Several uploaded log sources are independently high risk, which may indicate a broader incident pattern.",
                        "severity": "high",
                        "related_lines": [],
                        "source_names": suspicious_sources,
                    }
                )

        return insights[:8]

    def _highest_severity(self, items: list[dict]) -> str:
        order = ["critical", "high", "medium", "low"]
        severities = {item.get("severity", "low") for item in items}
        for severity in order:
            if severity in severities:
                return severity
        return "low"

    def _safe_value(self, value: str) -> str:
        return value if len(value) <= 16 else f"{value[:4]}...{value[-4:]}"
