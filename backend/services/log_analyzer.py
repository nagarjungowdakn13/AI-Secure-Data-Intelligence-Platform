from __future__ import annotations

import re


class LogAnalyzer:
    ERROR_PATTERN = re.compile(r"\b(error|exception|traceback|stack trace|fatal|nullpointerexception)\b", re.IGNORECASE)
    FAILURE_PATTERN = re.compile(r"\b(failed|failure|failures|denied|unauthorized|invalid login|forbidden)\b", re.IGNORECASE)
    SUSPICIOUS_PATTERN = re.compile(r"\b(exec|powershell|cmd\.exe|wget|curl|nmap|whoami)\b", re.IGNORECASE)

    def analyze(self, content: str, source_name: str, start_line: int = 1) -> list[dict]:
        findings: list[dict] = []
        failure_streak = 0

        for offset, line in enumerate(content.splitlines()):
            line_number = start_line + offset
            normalized = line.strip()
            if not normalized:
                continue

            if self.ERROR_PATTERN.search(normalized):
                findings.append(
                    self._build_finding(
                        label="stack_trace",
                        category="security_issue",
                        severity="medium",
                        line_number=line_number,
                        matched_text=normalized,
                        explanation="Stack traces or exception details may leak internal system information.",
                        source_name=source_name,
                    )
                )

            if self.FAILURE_PATTERN.search(normalized):
                failure_streak += 1
                findings.append(
                    self._build_finding(
                        label="repeated_failure",
                        category="security_issue",
                        severity="medium" if failure_streak < 3 else "high",
                        line_number=line_number,
                        matched_text=normalized,
                        explanation="Authentication or authorization failures may indicate abuse or misconfiguration.",
                        source_name=source_name,
                    )
                )
            else:
                failure_streak = 0

            if self.SUSPICIOUS_PATTERN.search(normalized):
                findings.append(
                    self._build_finding(
                        label="suspicious_pattern",
                        category="security_issue",
                        severity="high",
                        line_number=line_number,
                        matched_text=normalized,
                        explanation="Potentially suspicious command execution or reconnaissance pattern detected in logs.",
                        source_name=source_name,
                    )
                )

        return findings

    def _build_finding(self, *, label: str, category: str, severity: str, line_number: int, matched_text: str, explanation: str, source_name: str) -> dict:
        return {
            "category": category,
            "label": label,
            "severity": severity,
            "line_number": line_number,
            "matched_text": matched_text,
            "masked_text": matched_text,
            "confidence": 0.9,
            "explanation": explanation,
            "source_name": source_name,
        }
