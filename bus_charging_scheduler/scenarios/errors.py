"""Scenario loading and validation errors."""


class ScenarioValidationError(Exception):
    """Raised when a scenario fails structural or semantic validation."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        detail = "; ".join(messages)
        super().__init__(detail)
