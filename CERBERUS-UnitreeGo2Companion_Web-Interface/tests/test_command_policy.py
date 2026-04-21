
from backend.controller_contract.command_policy import CommandPolicy

def test_policy_blocks_without_bridge():
    policy = CommandPolicy()

    state = {
        "hardware": {"mode": "real"},
        "bridge": {"connected": False},
        "session": {"active": True},
        "safety": {"estop": False},
    }

    policy.update(state)
    assert policy.restricted is True
    assert "always" in policy.allowed_categories
