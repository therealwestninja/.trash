from __future__ import annotations

from typing import Any

from .models_runtime import ActionRequest, ActionResult, ActionStatus, ActionType, RuntimeState


class ActionResolver:
    """Convert operator text into a small, deterministic action set."""

    GREETING_WORDS = ("hello", "hi", "hey", "greet")
    STOP_WORDS = ("stop", "halt", "freeze", "estop")
    MOVE_WORDS = ("move", "walk", "go", "forward", "back", "left", "right")
    LOOK_WORDS = ("look", "scan", "search", "what", "why", "how", "where")
    FOLLOW_WORDS = ("follow", "come with", "track me", "stay with me")

    def resolve(self, text: str, state: RuntimeState | None = None) -> ActionRequest:
        cleaned = " ".join(text.strip().lower().split())
        if not cleaned:
            return ActionRequest(action=ActionType.IDLE, reason="empty_input")

        if any(word in cleaned for word in self.STOP_WORDS):
            return ActionRequest(action=ActionType.STOP, reason="operator_stop_request")

        if any(phrase in cleaned for phrase in self.FOLLOW_WORDS):
            return ActionRequest(action=ActionType.FOLLOW, reason="operator_follow_request")

        if any(word in cleaned for word in self.GREETING_WORDS):
            return ActionRequest(action=ActionType.GREET, reason="operator_greeting")

        if any(word in cleaned for word in self.MOVE_WORDS):
            params = self._extract_move_parameters(cleaned)
            return ActionRequest(
                action=ActionType.MOVE,
                reason="operator_motion_request",
                parameters=params,
            )

        if any(word in cleaned for word in self.LOOK_WORDS) or "?" in text:
            return ActionRequest(action=ActionType.LOOK, reason="operator_attention_request")

        return ActionRequest(action=ActionType.IDLE, reason="no_specific_action")

    def execute(self, request: ActionRequest, state: RuntimeState) -> ActionResult:
        action = request.action

        if action == ActionType.STOP:
            return ActionResult(
                action=action,
                status=ActionStatus.COMPLETED,
                reason="motion_stopped",
                parameters=request.parameters,
                output={"motion_state": "stopped"},
            )

        if action == ActionType.GREET:
            return ActionResult(
                action=action,
                status=ActionStatus.COMPLETED,
                reason="greeting_acknowledged",
                parameters=request.parameters,
                output={"speech": "Hello from Sweetie-Bot."},
            )

        if action == ActionType.MOVE:
            motion_state = f"move:{request.parameters.get('direction', 'forward')}"
            return ActionResult(
                action=action,
                status=ActionStatus.COMPLETED,
                reason="simulated_motion_request",
                parameters=request.parameters,
                output={"motion_state": motion_state},
            )

        if action == ActionType.LOOK:
            return ActionResult(
                action=action,
                status=ActionStatus.COMPLETED,
                reason="attention_shifted",
                parameters=request.parameters,
                output={"motion_state": "scanning"},
            )

        if action == ActionType.FOLLOW:
            return ActionResult(
                action=action,
                status=ActionStatus.COMPLETED,
                reason="follow_mode_requested",
                parameters=request.parameters,
                output={"motion_state": "following"},
            )

        return ActionResult(
            action=ActionType.IDLE,
            status=ActionStatus.COMPLETED,
            reason="idle_maintained",
            parameters=request.parameters,
            output={"motion_state": "idle"},
        )

    def _extract_move_parameters(self, cleaned: str) -> dict[str, Any]:
        direction = "forward"
        if "back" in cleaned:
            direction = "backward"
        elif "left" in cleaned:
            direction = "left"
        elif "right" in cleaned:
            direction = "right"

        speed = 0.25
        if "fast" in cleaned:
            speed = 0.6
        elif "slow" in cleaned:
            speed = 0.1

        return {
            "direction": direction,
            "speed": speed,
        }
