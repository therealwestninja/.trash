from time import time

from controller.app.runtime_manager import RuntimeManager


def test_stale_session_triggers_degraded_state_and_disarm():
    manager = RuntimeManager()
    lease = manager.acquire_session("ui")
    assert lease["owner"] == "ui"

    manager.session_leases.lease.expires_at = time() - 1
    state = manager.get_state()

    assert state["session"]["degraded"] is True
    assert state["diagnostics"]["summary"]["degraded"] is True
    assert state["safety"]["armed"] is False
