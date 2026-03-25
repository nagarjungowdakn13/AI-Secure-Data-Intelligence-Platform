from __future__ import annotations


class MaskingService:
    def mask_value(self, value: str) -> str:
        if len(value) <= 4:
            return "*" * len(value)
        return "*" * min(len(value), 12)

    def mask_content(self, content: str, findings: list[dict]) -> str:
        masked = content
        values_to_mask = {
            finding["matched_text"]
            for finding in findings
            if finding.get("matched_text") and finding.get("category") in {"secret", "sensitive_data"}
        }
        for value in sorted(values_to_mask, key=len, reverse=True):
            masked = masked.replace(value, self.mask_value(value))
        return masked
