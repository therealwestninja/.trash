from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from tests.conftest import PLUGIN_BY_NAME


STATEFUL_PLUGINS = {
    "sweetie-plugin-event-bus": ("event.publish", lambda i: {"topic": "race.topic", "source": "tests", "payload": {"i": i}}),
    "sweetie-plugin-memory-alaya": ("memory.store_episode", lambda i: {"text": f"episode-{i}", "tags": ["race"]}),
    "sweetie-plugin-world-model": ("world.upsert_object", lambda i: {"id": f"obj-{i}", "label": "marker", "position": {"x": float(i), "y": 0.0, "z": 0.0}}),
    "sweetie-plugin-payload-bus": ("payload.register", lambda i: {"id": f"payload-{i}", "name": f"Payload {i}", "base_url": f"http://payload-{i}.local", "capabilities": ["cap.race"]}),
}


@pytest.mark.concurrency
@pytest.mark.parametrize("plugin_name", sorted(STATEFUL_PLUGINS))
def test_parallel_execute_requests_remain_available(plugin_name, plugin_client_factory):
    plugin = PLUGIN_BY_NAME[plugin_name]
    client = plugin_client_factory(plugin)
    action, builder = STATEFUL_PLUGINS[plugin_name]

    def send(i: int):
        return client.post(plugin.entrypoints.get("execute", "/execute"), json={"type": action, "payload": builder(i)})

    with ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(send, range(25)))

    assert all(response.status_code < 500 for response in responses)

    status = client.get(plugin.entrypoints.get("health", "/health"))
    assert status.status_code == 200


@pytest.mark.concurrency
def test_event_bus_subscribe_publish_poll_under_parallel_load(plugin_client_factory):
    plugin = PLUGIN_BY_NAME["sweetie-plugin-event-bus"]
    client = plugin_client_factory(plugin)

    assert client.post("/execute", json={"type": "event.subscribe", "payload": {"subscriber_id": "parallel-sub", "topics": ["parallel.topic"]}}).status_code < 500

    def publish(i: int):
        return client.post("/execute", json={"type": "event.publish", "payload": {"topic": "parallel.topic", "source": "race", "payload": {"i": i}}})

    with ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(publish, range(30)))

    assert all(response.status_code < 500 for response in responses)
    poll = client.post("/execute", json={"type": "event.poll", "payload": {"subscriber_id": "parallel-sub", "limit": 100}})
    assert poll.status_code < 500
    assert isinstance(poll.json(), dict)
