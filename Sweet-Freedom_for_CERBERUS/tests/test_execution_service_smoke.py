from controller.app.runtime_execution import (
    create_goal_for_text,
    make_accepted_feedback,
    make_blocked_feedback,
    make_canceled_feedback,
)


class DummyAction:
    action = "greet"


def test_execution_helpers_build_expected_goal_and_feedback():
    goal = create_goal_for_text(DummyAction(), text="hello sweetie", requested_by="ui")
    assert goal.action_type == "greet"
    accepted = make_accepted_feedback(goal)
    blocked = make_blocked_feedback(goal, "blocked")
    canceled = make_canceled_feedback(goal.goal_id, "ui")

    assert accepted.status == "accepted"
    assert blocked.status == "blocked"
    assert canceled.status == "canceled"
