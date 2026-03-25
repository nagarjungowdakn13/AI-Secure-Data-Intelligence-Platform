from __future__ import annotations

import json
import os

import httpx


class AIService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = float(os.getenv("OPENAI_TIMEOUT", "20"))

    def generate_insights(self, *, content: str, findings: list[dict], risk_assessment: dict, input_type: str) -> dict:
        if self.api_key:
            try:
                return self._generate_remote(content, findings, risk_assessment, input_type)
            except Exception:
                return self._generate_fallback(content, findings, risk_assessment, input_type)
        return self._generate_fallback(content, findings, risk_assessment, input_type)

    def _generate_remote(self, content: str, findings: list[dict], risk_assessment: dict, input_type: str) -> dict:
        prompt = {
            "role": "system",
            "content": (
                "You are a security analysis assistant. Return JSON with keys "
                "'summary' and 'insights'. Insights must contain title and detail."
            ),
        }
        user_message = {
            "role": "user",
            "content": json.dumps(
                {
                    "input_type": input_type,
                    "risk_assessment": risk_assessment,
                    "findings": findings[:25],
                    "content_preview": content[:3000],
                }
            ),
        }
        response = httpx.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [prompt, user_message],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        parsed = json.loads(payload["choices"][0]["message"]["content"])
        return {"summary": parsed.get("summary", "AI-generated analysis completed."), "insights": parsed.get("insights", [])}

    def _generate_fallback(self, content: str, findings: list[dict], risk_assessment: dict, input_type: str) -> dict:
        severity_counts = {}
        label_counts = {}
        for finding in findings:
            severity_counts[finding["severity"]] = severity_counts.get(finding["severity"], 0) + 1
            label_counts[finding["label"]] = label_counts.get(finding["label"], 0) + 1

        top_labels = ", ".join(
            f"{label} ({count})" for label, count in sorted(label_counts.items(), key=lambda item: item[1], reverse=True)[:4]
        ) or "no sensitive indicators"
        preview_lines = [line.strip() for line in content.splitlines() if line.strip()][:5]
        preview = " | ".join(preview_lines)[:250] or "No substantial content preview available."

        return {
            "summary": (
                f"Analyzed {input_type} content and found {len(findings)} notable indicators. "
                f"Overall risk is {risk_assessment['risk_level']} with a score of {risk_assessment['risk_score']}. "
                f"Primary signals: {top_labels}."
            ),
            "insights": [
                {"title": "Activity Summary", "detail": f"Observed activity preview: {preview}"},
                {
                    "title": "Risk Explanation",
                    "detail": (
                        f"Risk is {risk_assessment['risk_level']} with "
                        f"{severity_counts.get('critical', 0)} critical, "
                        f"{severity_counts.get('high', 0)} high, "
                        f"{severity_counts.get('medium', 0)} medium, and "
                        f"{severity_counts.get('low', 0)} low findings."
                    ),
                },
                {
                    "title": "Anomaly Insight",
                    "detail": (
                        "Repeated failures, stack traces, and credentials in logs can leak "
                        "internal context and increase incident impact."
                    ),
                },
            ],
        }
