from __future__ import annotations


class RiskEngine:
    severity_weights = {
        "critical": 40,
        "high": 25,
        "medium": 15,
        "low": 5,
    }

    def merge_findings(self, findings: list[dict]) -> list[dict]:
        deduped = []
        seen = set()
        for finding in findings:
            key = (
                finding["label"],
                finding.get("line_number"),
                finding["matched_text"],
                finding["source_name"],
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(finding)
        return deduped

    def score(self, findings: list[dict]) -> dict:
        raw_score = sum(self.severity_weights.get(finding["severity"], 0) for finding in findings)
        risk_score = min(100, raw_score)
        breakdown = self._breakdown(findings)

        if breakdown["critical"] > 0:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        elif risk_score > 0:
            risk_level = "low"
        else:
            risk_level = "informational"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_breakdown": breakdown,
            "recommendations": self._recommendations(findings, risk_level),
        }

    def _breakdown(self, findings: list[dict]) -> dict:
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            severity = finding.get("severity")
            if severity in breakdown:
                breakdown[severity] += 1
        return breakdown

    def _recommendations(self, findings: list[dict], risk_level: str) -> list[str]:
        recommendations: list[str] = []
        labels = {finding["label"] for finding in findings}

        if {"password", "api_key", "token", "secret_key", "client_secret", "private_key", "high_entropy_secret"} & labels:
            recommendations.append("Rotate exposed credentials immediately and invalidate any active sessions or tokens.")
        if {"stack_trace", "connection_string", "credential_hint"} & labels:
            recommendations.append("Sanitize application logs and remove internal implementation details from user-visible outputs.")
        if {"repeated_failure", "suspicious_pattern", "ip_address"} & labels:
            recommendations.append("Review source IP activity, rate-limit repeated failures, and confirm no brute-force or abuse pattern is active.")
        if "credit_card" in labels:
            recommendations.append("Treat the affected records as regulated payment data and follow PCI-safe handling and redaction controls.")
        if risk_level in {"high", "critical"}:
            recommendations.append("Escalate to security review and block distribution of this content until remediation is complete.")

        if not recommendations:
            recommendations.append("No urgent remediation required; continue monitoring and retain masking for analyst review.")

        return recommendations[:4]
