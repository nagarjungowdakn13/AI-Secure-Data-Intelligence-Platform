class PolicyEngine:
    def determine_action(self, *, risk_level: str, block_high_risk: bool) -> str:
        if risk_level == "critical":
            return "block_and_alert"
        if risk_level == "high":
            return "block_and_alert" if block_high_risk else "review_required"
        if risk_level == "medium":
            return "review_required"
        if risk_level == "low":
            return "allow_with_masking"
        return "allow"
