from typing import Any

from .animation_runtime import AnimationRuntime
from .emotion_runtime import EmotionRuntime
from .expression_runtime import ExpressionRuntime
from .presence_runtime import PresenceRuntime


class RuntimePipeline:
    def __init__(self) -> None:
        self.emotion = EmotionRuntime()
        self.presence = PresenceRuntime()
        self.expression = ExpressionRuntime()
        self.animation = AnimationRuntime()

    def process(self, text: str) -> dict[str, Any]:
        emotion = self.emotion.process_text(text)
        presence = self.presence.tick(emotion)
        expression = self.expression.resolve(emotion, presence)
        animation = self.animation.resolve_for_expression(expression)

        return {
            "emotion": emotion,
            "presence": presence,
            "expression": expression,
            "animation": animation,
        }
