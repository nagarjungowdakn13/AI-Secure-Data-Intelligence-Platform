from __future__ import annotations

import re

from backend.services.masking_service import MaskingService


class RegexDetector:
    def __init__(self) -> None:
        self.masking_service = MaskingService()
        self.patterns = [
            {
                "label": "email",
                "category": "sensitive_data",
                "severity": "low",
                "pattern": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
                "explanation": "Email address detected in content.",
            },
            {
                "label": "phone",
                "category": "sensitive_data",
                "severity": "low",
                "pattern": re.compile(r"(?:(?:\+?\d{1,3})?[-.\s(]*)?(?:\d{3}[-.\s)]*){2}\d{4}\b"),
                "explanation": "Phone number detected in content.",
            },
            {
                "label": "api_key",
                "category": "secret",
                "severity": "high",
                "pattern": re.compile(r"(?i)(?:api[_-]?key\s*[:=]\s*([A-Za-z0-9_\-.]{8,})|\b(?:sk|pk|rk)[-_][A-Za-z0-9_-]{8,}\b|\bAKIA[0-9A-Z]{16}\b)"),
                "explanation": "API key-like token detected.",
            },
            {
                "label": "password",
                "category": "secret",
                "severity": "critical",
                "pattern": re.compile(r"(?i)\bpassword\s*[:=]\s*([^\s\"']+)"),
                "explanation": "Password assignment detected.",
            },
            {
                "label": "token",
                "category": "secret",
                "severity": "high",
                "pattern": re.compile(r"(?i)\b(?:token|bearer)\s*[:=]?\s*([A-Za-z0-9\-_.=]{8,})"),
                "explanation": "Access token or bearer token detected.",
            },
            {
                "label": "secret_key",
                "category": "secret",
                "severity": "high",
                "pattern": re.compile(r"(?i)\b(?:secret[_-]?key|secret)\s*[:=]\s*([^\s\"']{8,})"),
                "explanation": "Secret key assignment detected.",
            },
            {
                "label": "client_secret",
                "category": "secret",
                "severity": "high",
                "pattern": re.compile(r"(?i)\bclient[_-]?secret\s*[:=]\s*([^\s\"']{8,})"),
                "explanation": "Client secret detected.",
            },
            {
                "label": "connection_string",
                "category": "security_issue",
                "severity": "high",
                "pattern": re.compile(r"(?i)\b(?:server|host)=.+;(?:database|db)=.+;(?:user id|uid|user)=.+;(?:password|pwd)=.+"),
                "explanation": "Database connection string with embedded credentials detected.",
            },
            {
                "label": "credit_card",
                "category": "sensitive_data",
                "severity": "high",
                "pattern": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
                "explanation": "Potential payment card number detected.",
            },
            {
                "label": "ip_address",
                "category": "sensitive_data",
                "severity": "low",
                "pattern": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
                "explanation": "IP address detected in content.",
            },
            {
                "label": "private_key",
                "category": "secret",
                "severity": "critical",
                "pattern": re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
                "explanation": "Private key material detected.",
            },
        ]

    def scan_content(self, content: str, source_name: str, start_line: int = 1) -> list[dict]:
        findings: list[dict] = []
        for offset, line in enumerate(content.splitlines()):
            line_number = start_line + offset
            findings.extend(self._scan_line(line, line_number, source_name))
        return findings

    def _scan_line(self, line: str, line_number: int, source_name: str) -> list[dict]:
        matches: list[dict] = []
        for pattern_config in self.patterns:
            for match in pattern_config["pattern"].finditer(line):
                matched_value = self._extract_value(match, pattern_config["label"])
                matches.append(
                    {
                        "category": pattern_config["category"],
                        "label": pattern_config["label"],
                        "severity": pattern_config["severity"],
                        "line_number": line_number,
                        "matched_text": matched_value,
                        "masked_text": self.masking_service.mask_value(matched_value),
                        "confidence": 0.97,
                        "explanation": pattern_config["explanation"],
                        "source_name": source_name,
                    }
                )

        matches.extend(self._detect_contextual_entities(line, line_number, source_name))
        matches.extend(self._detect_high_entropy_secret(line, line_number, source_name))
        return matches

    def _extract_value(self, match: re.Match, label: str) -> str:
        if label in {"api_key", "password", "token", "secret_key", "client_secret"} and match.lastindex and match.group(1):
            return match.group(1)
        return match.group(0)

    def _detect_contextual_entities(self, line: str, line_number: int, source_name: str) -> list[dict]:
        contextual_patterns = {
            "username": ("sensitive_data", "low", r"(?i)\b(?:user|username)\s*[:=]\s*([^\s\"']+)"),
            "credential_hint": ("security_issue", "medium", r"(?i)\b(?:credential|secret|auth)\b"),
        }
        results: list[dict] = []
        for label, (category, severity, pattern) in contextual_patterns.items():
            match = re.search(pattern, line)
            if not match:
                continue
            value = match.group(1) if match.lastindex else match.group(0)
            results.append(
                {
                    "category": category,
                    "label": label,
                    "severity": severity,
                    "line_number": line_number,
                    "matched_text": value,
                    "masked_text": self.masking_service.mask_value(value),
                    "confidence": 0.75,
                    "explanation": "Contextual entity detected through lightweight NER-style pattern matching.",
                    "source_name": source_name,
                }
            )
        return results

    def _detect_high_entropy_secret(self, line: str, line_number: int, source_name: str) -> list[dict]:
        match = re.search(r"(?i)\b(?:secret|token|key)\b\s*[:=]\s*([A-Za-z0-9+/=_\-]{20,})", line)
        if not match:
            return []

        candidate = match.group(1)
        unique_ratio = len(set(candidate)) / max(len(candidate), 1)
        if unique_ratio < 0.45:
            return []

        return [
            {
                "category": "secret",
                "label": "high_entropy_secret",
                "severity": "high",
                "line_number": line_number,
                "matched_text": candidate,
                "masked_text": self.masking_service.mask_value(candidate),
                "confidence": 0.82,
                "explanation": "High-entropy secret-like value detected through heuristic analysis.",
                "source_name": source_name,
            }
        ]
