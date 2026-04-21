from fastapi import APIRouter

from .routes_v2 import (
    arm_system,
    cancel_action,
    capabilities,
    capability_detail,
    clear_estop,
    clear_recording,
    diagnostics,
    disarm_system,
    export_recording,
    health,
    lock_control_source,
    operator_text,
    presence_tick,
    quick_action,
    ready,
    recover_lifecycle,
    replay_clear,
    replay_load,
    replay_state,
    replay_step,
    runtime_full_state,
    session_acquire,
    session_checkin,
    session_release,
    session_state,
    trigger_estop,
    unlock_control_source,
)

router_v1 = APIRouter(prefix="/api/v1")

router_v1.add_api_route("/operator/text", operator_text, methods=["POST"])
router_v1.add_api_route("/action/quick", quick_action, methods=["POST"])
router_v1.add_api_route("/action/cancel", cancel_action, methods=["POST"])
router_v1.add_api_route("/control/lock", lock_control_source, methods=["POST"])
router_v1.add_api_route("/control/unlock", unlock_control_source, methods=["POST"])
router_v1.add_api_route("/lifecycle/recover", recover_lifecycle, methods=["POST"])
router_v1.add_api_route("/safety/arm", arm_system, methods=["POST"])
router_v1.add_api_route("/safety/disarm", disarm_system, methods=["POST"])
router_v1.add_api_route("/safety/estop", trigger_estop, methods=["POST"])
router_v1.add_api_route("/safety/clear_estop", clear_estop, methods=["POST"])
router_v1.add_api_route("/diagnostics", diagnostics, methods=["GET"])
router_v1.add_api_route("/capabilities", capabilities, methods=["GET"])
router_v1.add_api_route("/capabilities/{capability_id}", capability_detail, methods=["GET"])
router_v1.add_api_route("/recording/export", export_recording, methods=["GET"])
router_v1.add_api_route("/recording/clear", clear_recording, methods=["POST"])
router_v1.add_api_route("/replay/load", replay_load, methods=["POST"])
router_v1.add_api_route("/replay/step", replay_step, methods=["POST"])
router_v1.add_api_route("/replay/state", replay_state, methods=["GET"])
router_v1.add_api_route("/replay/clear", replay_clear, methods=["POST"])
router_v1.add_api_route("/session/acquire", session_acquire, methods=["POST"])
router_v1.add_api_route("/session/checkin", session_checkin, methods=["POST"])
router_v1.add_api_route("/session/release", session_release, methods=["POST"])
router_v1.add_api_route("/session/state", session_state, methods=["GET"])
router_v1.add_api_route("/runtime/state", runtime_full_state, methods=["GET"])
router_v1.add_api_route("/presence/tick", presence_tick, methods=["POST"])
router_v1.add_api_route("/health", health, methods=["GET"])
router_v1.add_api_route("/ready", ready, methods=["GET"])
