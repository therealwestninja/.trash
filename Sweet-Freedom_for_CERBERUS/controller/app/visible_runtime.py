from typing import Any

from .runtime_pipeline import RuntimePipeline


class VisibleRuntime:
    def __init__(self) -> None:
        self.pipeline = RuntimePipeline()
        self.state: dict[str, Any] = {}

    def process(self, text: str) -> dict[str, Any]:
        self.state = self.pipeline.process(text)
        return self.state

    def status(self) -> dict[str, Any]:
        return self.state
