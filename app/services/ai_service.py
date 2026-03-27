class AIService:
    @staticmethod
    def improve_justification(text):
        enhanced = f"Business Context: {text.strip()}\nRisk Framing: Potential financial and compliance impact has been evaluated.\nRequest: Please review and approve based on operational need."
        return enhanced

    @staticmethod
    def generate_summary(payload):
        title = payload.get("title", "Untitled Exception")
        amount = payload.get("amount", 0)
        exception_type = payload.get("exception_type", "UNKNOWN")
        return f"{title} ({exception_type}) with estimated impact of {amount}. Requires workflow review."

    @staticmethod
    def check_missing_fields(payload):
        required = ["title", "description", "justification", "amount", "exception_type_id", "store_id"]
        missing = [field for field in required if not payload.get(field)]
        if not missing:
            return "No missing fields detected."
        return f"Missing required fields: {', '.join(missing)}"
