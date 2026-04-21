from __future__ import annotations

from typing import Any

from .action_models import ActionFeedback, ActionGoal, ActionResult, GoalStatus


def create_goal_for_text(requested_action: Any, *, text: str, requested_by: str) -> ActionGoal:
    return ActionGoal(
        action_type=getattr(requested_action, "action", None)
        or getattr(requested_action, "action_type", None)
        or "unknown",
        params={"text": text},
        requested_by=requested_by,
    )


def make_accepted_feedback(goal: ActionGoal) -> ActionFeedback:
    return ActionFeedback(
        goal_id=goal.goal_id,
        status=GoalStatus.ACCEPTED,
        progress=0.1,
        phase="accepted",
        message=f"Accepted action '{goal.action_type}'",
    )


def make_blocked_feedback(goal: ActionGoal, reason: str) -> ActionFeedback:
    return ActionFeedback(
        goal_id=goal.goal_id,
        status=GoalStatus.BLOCKED,
        progress=1.0,
        phase="blocked",
        message=reason,
    )


def make_running_feedback(goal: ActionGoal) -> ActionFeedback:
    return ActionFeedback(
        goal_id=goal.goal_id,
        status=GoalStatus.RUNNING,
        progress=0.5,
        phase="executing",
        message=f"Executing action '{goal.action_type}'",
    )


def make_completed_feedback(goal: ActionGoal) -> ActionFeedback:
    return ActionFeedback(
        goal_id=goal.goal_id,
        status=GoalStatus.COMPLETED,
        progress=1.0,
        phase="completed",
        message=f"Completed action '{goal.action_type}'",
    )


def make_completed_result(goal: ActionGoal, action_result: Any) -> ActionResult:
    return ActionResult(
        goal_id=goal.goal_id,
        status=GoalStatus.COMPLETED,
        success=True,
        code="completed",
        message=getattr(action_result, "message", "Action completed"),
        details=action_result.model_dump(mode="json") if hasattr(action_result, "model_dump") else {},
    )


def make_blocked_result(goal: ActionGoal, reason: str, *, code: str = "blocked", details: dict | None = None) -> ActionResult:
    return ActionResult(
        goal_id=goal.goal_id,
        status=GoalStatus.BLOCKED,
        success=False,
        code=code,
        message=reason,
        details=details or {},
    )


def make_canceled_feedback(goal_id: str, requested_by: str) -> ActionFeedback:
    return ActionFeedback(
        goal_id=goal_id,
        status=GoalStatus.CANCELED,
        progress=1.0,
        phase="canceled",
        message=f"Goal canceled by {requested_by}",
    )


def make_canceled_result(goal_id: str, requested_by: str) -> ActionResult:
    return ActionResult(
        goal_id=goal_id,
        status=GoalStatus.CANCELED,
        success=False,
        code="canceled",
        message=f"Goal canceled by {requested_by}",
        details={"requested_by": requested_by},
    )
