import asyncio

from controller.app.event_publisher import publish_named_event, publish_runtime_bundle, publish_session_bundle


def test_event_publisher_functions_are_awaitable():
    async def run():
        await publish_named_event("test_event", {"ok": True})
        await publish_runtime_bundle({"command_mux": {}, "diagnostics": {}, "lifecycle": {}})
        await publish_session_bundle({"active": False}, {"phase": "ready"})
    asyncio.run(run())
