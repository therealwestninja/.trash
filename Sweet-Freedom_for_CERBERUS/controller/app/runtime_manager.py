from __future__ import annotations

from typing import Any

from .action_system import ActionResolver
from .command_mux import CommandMux
from .models_runtime import OperatorInput, RuntimeMode, RuntimeState
from .runtime_execution import (
    create_goal_for_text,
    make_accepted_feedback,
    make_blocked_feedback,
    make_blocked_result,
    make_canceled_feedback,
    make_canceled_result,
    make_completed_feedback,
    make_completed_result,
    make_running_feedback,
)
from .runtime_history import append_history_entry
from .runtime_lifecycle import RuntimeLifecycleManager
from .runtime_pipeline import RuntimePipeline
from .runtime_recording import record_runtime_event
from .runtime_state_builder import build_runtime_state_payload
from .safety_policy import SafetyPolicy
from .session_lease import SessionLeaseManager
from .session_recorder import session_recorder


class RuntimeManager:
    def __init__(self) -> None:
        self.pipeline = RuntimePipeline()
        self.action_resolver = ActionResolver()
        self.safety_policy = SafetyPolicy(hardware_mode=RuntimeMode.SIMULATION)
        self.session_leases = SessionLeaseManager()
        self.command_mux = CommandMux()
        self.lifecycle = RuntimeLifecycleManager()
        self.last_state = RuntimeState(mode=RuntimeMode.SIMULATION)
        self.command_history: list[dict[str, Any]] = []
        self.motion_state: str = "idle"
        self.active_goal = None
        self.last_feedback = None
        self.last_result = None
        self.is_degraded: bool = False
        self.lifecycle.set_ready("runtime initialized")

    def _apply_comms_loss_policy_if_needed(self) -> None:
        if not self.session_leases.is_stale():
            if self.is_degraded:
                self.lifecycle.set_ready("session restored")
            self.is_degraded = False
            return

        self.is_degraded = True
        policy = self.session_leases.policy.on_timeout
        if "controlled_stop" in policy:
            self.motion_state = "stopped"
        if "disarm" in policy:
            self.safety_policy.disarm()
        self.lifecycle.set_degraded("stale session / comms-loss policy active")
        record_runtime_event("comms_loss_policy_applied", {
            "policy": policy,
            "session": self.session_leases.get_state(),
        })

    def process_text(self, text: str, requested_by: str = "ui") -> dict[str, Any]:
        self._apply_comms_loss_policy_if_needed()

        source_name = "quick_action" if requested_by == "quick_action" else "ui"
        allowed_source, source_reason = self.command_mux.can_accept(source_name)

        pipeline_state = self.pipeline.process(text)
        requested_action = self.action_resolver.resolve(text, self.last_state)

        goal = create_goal_for_text(requested_action, text=text, requested_by=requested_by)
        self.active_goal = goal
        self.last_feedback = make_accepted_feedback(goal)

        if self.is_degraded:
            source_reason = "System is degraded due to stale session"
            allowed_source = False

        if not allowed_source:
            self.last_feedback = make_blocked_feedback(goal, source_reason)
            self.last_result = make_blocked_result(
                goal,
                source_reason,
                code="source_blocked",
                details={"active_source": self.command_mux.active_source, "degraded": self.is_degraded},
            )
            action_result = self.safety_policy.make_blocked_result(requested_action, source_reason)
            self.motion_state = "blocked"
            if self.is_degraded:
                self.lifecycle.set_degraded(source_reason)
        else:
            allowed, reason = self.safety_policy.evaluate(requested_action)
            if allowed:
                self.lifecycle.set_engaged(f"executing {goal.action_type}")
                self.last_feedback = make_running_feedback(goal)
                action_result = self.action_resolver.execute(requested_action, self.last_state)
                self.last_feedback = make_completed_feedback(goal)
                self.last_result = make_completed_result(goal, action_result)
                if not self.is_degraded:
                    self.lifecycle.set_ready(f"completed {goal.action_type}")
            else:
                action_result = self.safety_policy.make_blocked_result(requested_action, reason)
                self.last_feedback = make_blocked_feedback(goal, reason)
                self.last_result = make_blocked_result(
                    goal,
                    reason,
                    code="blocked",
                    details=action_result.model_dump(mode="json") if hasattr(action_result, "model_dump") else {},
                )
                if "E-Stop" in reason:
                    self.lifecycle.set_faulted(reason)
            self.motion_state = self._derive_motion_state(requested_action, action_result)

        self.command_history = append_history_entry(
            self.command_history,
            text=text,
            goal=goal.model_dump(mode="json"),
            feedback=self.last_feedback.model_dump(mode="json") if self.last_feedback else None,
            result=self.last_result.model_dump(mode="json") if self.last_result else None,
            action=requested_action.model_dump(mode="json"),
            motion_state=self.motion_state,
            control_source=self.command_mux.active_source,
            degraded=self.is_degraded,
            lifecycle=self.lifecycle.snapshot(),
        )

        self.last_state = RuntimeState(
            mode=self.last_state.mode,
            operator_input=OperatorInput(text=text),
            emotion=pipeline_state["emotion"],
            presence=pipeline_state["presence"],
            expression=pipeline_state["expression"],
            animation=pipeline_state["animation"],
            current_action=requested_action,
            last_action_result=action_result,
            safety=self.safety_policy.snapshot(),
            notes=[],
        )
        state = self.get_state()
        record_runtime_event("operator_text", {"text": text, "state": state})
        return state

    def cancel_goal(self, goal_id: str, requested_by: str = "ui") -> dict[str, Any] | None:
        if not self.active_goal or self.active_goal.goal_id != goal_id:
            return None

        self.last_feedback = make_canceled_feedback(goal_id, requested_by)
        self.last_result = make_canceled_result(goal_id, requested_by)
        self.motion_state = "stopped"
        self.lifecycle.set_ready("goal canceled")

        self.command_history = append_history_entry(
            self.command_history,
            text="[cancel]",
            goal=self.active_goal.model_dump(mode="json"),
            feedback=self.last_feedback.model_dump(mode="json"),
            result=self.last_result.model_dump(mode="json"),
            action={"action": "cancel_goal"},
            motion_state=self.motion_state,
            control_source=self.command_mux.active_source,
            degraded=self.is_degraded,
            lifecycle=self.lifecycle.snapshot(),
        )
        state = self.get_state()
        record_runtime_event("goal_canceled", {"goal_id": goal_id, "state": state})
        return state

    def get_state(self) -> dict[str, Any]:
        self._apply_comms_loss_policy_if_needed()
        return build_runtime_state_payload(
            base_state=self.last_state.model_dump(mode="json"),
            motion_state=self.motion_state,
            command_history=self.command_history,
            active_goal=self.active_goal.model_dump(mode="json") if self.active_goal else None,
            last_feedback=self.last_feedback.model_dump(mode="json") if self.last_feedback else None,
            goal_result=self.last_result.model_dump(mode="json") if self.last_result else None,
            session=self.session_leases.get_state(),
            command_mux=self.command_mux.snapshot(),
            lifecycle=self.lifecycle.snapshot(),
            recording=session_recorder.snapshot(),
            is_degraded=self.is_degraded,
        )

    def lock_source(self, source_name: str) -> bool:
        ok = self.command_mux.lock(source_name)
        if ok:
            record_runtime_event("control_source_locked", {"source": source_name})
        return ok

    def unlock_source(self, source_name: str) -> bool:
        ok = self.command_mux.unlock(source_name)
        if ok:
            record_runtime_event("control_source_unlocked", {"source": source_name})
        return ok

    def arm_system(self) -> dict[str, Any]:
        self.last_state.safety = self.safety_policy.arm()
        if not self.is_degraded:
            self.lifecycle.set_ready("system armed")
        state = self.get_state()
        record_runtime_event("system_armed", {"state": state})
        return state

    def disarm_system(self) -> dict[str, Any]:
        self.last_state.safety = self.safety_policy.disarm()
        self.motion_state = "idle"
        if not self.is_degraded:
            self.lifecycle.set_ready("system disarmed")
        state = self.get_state()
        record_runtime_event("system_disarmed", {"state": state})
        return state

    def recover_lifecycle(self) -> dict[str, Any]:
        self.is_degraded = False
        self.lifecycle.recover()
        state = self.get_state()
        record_runtime_event("lifecycle_recovered", {"state": state})
        return state

    def tick_presence(self) -> dict[str, Any]:
        emotion = self.last_state.emotion or {}
        presence = self.pipeline.presence.tick(emotion)
        self.last_state.presence = presence
        record_runtime_event("presence_tick", {"presence": presence})
        return presence

    def trigger_estop(self) -> dict[str, Any]:
        self.last_state.safety = self.safety_policy.trigger_estop()
        self.motion_state = "estop"
        self.lifecycle.set_faulted("E-Stop latched")
        record_runtime_event("estop_triggered", {"safety": self.last_state.safety.model_dump(mode="json")})
        return self.last_state.safety.model_dump(mode="json")

    def clear_estop(self) -> dict[str, Any]:
        self.last_state.safety = self.safety_policy.clear_estop()
        self.motion_state = "idle"
        if not self.is_degraded:
            self.lifecycle.set_ready("E-Stop cleared")
        record_runtime_event("estop_cleared", {"safety": self.last_state.safety.model_dump(mode="json")})
        return self.last_state.safety.model_dump(mode="json")

    def acquire_session(self, owner: str = "ui") -> dict[str, Any]:
        lease = self.session_leases.acquire(owner).model_dump(mode="json")
        self.is_degraded = False
        self.lifecycle.set_ready("session acquired")
        record_runtime_event("session_acquired", {"lease": lease})
        return lease

    def session_checkin(self, lease_id: str) -> dict[str, Any] | None:
        lease = self.session_leases.checkin(lease_id)
        if lease:
            self.is_degraded = False
            self.lifecycle.set_ready("session keepalive restored")
            record_runtime_event("session_checkin", {"lease": lease.model_dump(mode="json")})
        return None if lease is None else lease.model_dump(mode="json")

    def release_session(self, lease_id: str) -> bool:
        ok = self.session_leases.release(lease_id)
        if ok:
            self.is_degraded = False
            self.lifecycle.set_ready("session released")
            record_runtime_event("session_released", {"lease_id": lease_id})
        return ok

    @staticmethod
    def _derive_motion_state(requested_action: Any, action_result: Any) -> str:
        action_name = getattr(requested_action, "action", None) or getattr(requested_action, "action_type", None) or "idle"
        result_status = getattr(action_result, "status", "unknown")
        if result_status == "blocked":
            return "blocked"
        if action_name in {"move", "move_forward", "follow"}:
            return "moving"
        if action_name == "stop":
            return "stopped"
        if action_name in {"look", "explore"}:
            return "scanning"
        return "idle"


runtime_manager = RuntimeManager()
