from __future__ import annotations

from typing import Any, Dict, List


VALID_EXECUTE_CASES: Dict[str, List[Dict[str, Any]]] = {
    "sweetie-plugin-action-registry": [
        {"type": "action.register", "payload": {"action_name": "test.wave", "target_plugin": "demo", "target_action": "robot.command"}},
        {"type": "action.get", "payload": {"action_name": "test.wave"}},
        {"type": "action.set_policy", "payload": {"action_name": "test.wave", "policy": {"mode": "safe"}}},
        {"type": "action.dispatch", "payload": {"action_name": "test.wave", "payload_override": {"speed": 0.2}}},
        {"type": "action.list", "payload": {}},
        {"type": "action.status", "payload": {}},
        {"type": "action.unregister", "payload": {"action_name": "test.wave"}},
    ],
    "sweetie-plugin-audio": [
        {"type": "audio.execute", "payload": {"clip": "bark", "volume": 0.5}},
    ],
    "sweetie-plugin-autonomy": [
        {"type": "autonomy.execute", "payload": {"mode": "patrol"}},
    ],
    "sweetie-plugin-cerberus-bridge": [
        {"type": "cerberus-bridge.execute", "payload": {"goal": "sit"}},
    ],
    "sweetie-plugin-character": [
        {"type": "character.execute", "payload": {"input": "hello"}},
    ],
    "sweetie-plugin-cognitive-core": [
        {"type": "cognition.perceive_event", "payload": {"event": {"topic": "human_wave", "source": "camera", "payload": {"distance_m": 1.2}}}},
        {"type": "cognition.evaluate_context", "payload": {"context": {"battery": 0.9, "human_distance_m": 1.4}}},
        {"type": "cognition.choose_action", "payload": {"context": {"human_detected": True, "battery": 0.8}}},
        {"type": "cognition.set_state", "payload": {"mood": "curious", "curiosity": 0.9}},
        {"type": "cognition.get_state", "payload": {}},
        {"type": "cognition.reset", "payload": {}},
        {"type": "cognition.status", "payload": {}},
    ],
    "sweetie-plugin-emotion": [
        {"type": "emotion.execute", "payload": {"state": "happy"}},
    ],
    "sweetie-plugin-event-bus": [
        {"type": "event.subscribe", "payload": {"subscriber_id": "test-sub", "topics": ["topic.alpha"]}},
        {"type": "event.publish", "payload": {"topic": "topic.alpha", "source": "tests", "payload": {"hello": "world"}}},
        {"type": "event.poll", "payload": {"subscriber_id": "test-sub", "limit": 5}},
        {"type": "event.recent", "payload": {"limit": 5}},
        {"type": "event.status", "payload": {}},
        {"type": "event.unsubscribe", "payload": {"subscriber_id": "test-sub"}},
        {"type": "event.clear", "payload": {}},
    ],
    "sweetie-plugin-gait-library": [
        {"type": "gait.list_profiles", "payload": {}},
        {"type": "gait.list_gaits", "payload": {"profile": "default"}},
        {"type": "gait.get_gait", "payload": {"profile": "default", "gait": "walk"}},
        {"type": "gait.set_active", "payload": {"profile": "default", "gait": "walk"}},
        {"type": "gait.get_active", "payload": {}},
        {"type": "gait.adapt_command", "payload": {"profile": "default", "command": {"speed": 0.2}}},
        {"type": "gait.preview_sequence", "payload": {"profile": "default", "seconds": 1.0}},
        {"type": "gait.status", "payload": {}},
    ],
    "sweetie-plugin-input": [
        {"type": "input.execute", "payload": {"source": "gamepad"}},
    ],
    "sweetie-plugin-interaction-core": [
        {"type": "interaction.process_event", "payload": {"event": {"type": "human_detected", "distance_m": 1.1}}},
        {"type": "interaction.get_state", "payload": {}},
        {"type": "interaction.reset", "payload": {}},
    ],
    "sweetie-plugin-leg-odometry": [
        {"type": "odom.update", "payload": {"vx": 0.3, "vy": 0.0, "yaw_rate": 0.1, "dt": 0.5}},
        {"type": "odom.get", "payload": {}},
        {"type": "odom.status", "payload": {}},
        {"type": "odom.reset", "payload": {}},
    ],
    "sweetie-plugin-memory": [
        {"type": "memory.execute", "payload": {"session_id": "s1", "key": "k", "value": "v"}},
    ],
    "sweetie-plugin-memory-alaya": [
        {"type": "memory.store_episode", "payload": {"text": "Saw a human", "tags": ["vision"]}},
        {"type": "memory.store_fact", "payload": {"text": "Charging dock is near kitchen", "tags": ["map"]}},
        {"type": "memory.query", "payload": {"text": "human", "limit": 5}},
        {"type": "memory.consolidate", "payload": {"min_tag_overlap": 1}},
        {"type": "memory.list", "payload": {}},
        {"type": "memory.status", "payload": {}},
    ],
    "sweetie-plugin-mission-bt": [
        {"type": "mission.start", "payload": {"name": "patrol"}},
        {"type": "mission.tick", "payload": {}},
        {"type": "mission.status", "payload": {}},
        {"type": "mission.stop", "payload": {}},
    ],
    "sweetie-plugin-nav2-pathing": [
        {"type": "nav.preview_route", "payload": {"start": {"x": 0, "y": 0}, "goal": {"x": 1, "y": 1}}},
        {"type": "nav.goal", "payload": {"x": 1.0, "y": 2.0, "yaw": 0.0}},
        {"type": "nav.follow_waypoints", "payload": {"waypoints": [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 1.0}] }},
        {"type": "nav.recovery", "payload": {"issue": "blocked"}},
        {"type": "nav.cancel", "payload": {}},
        {"type": "nav.status", "payload": {}},
    ],
    "sweetie-plugin-payload-bus": [
        {"type": "payload.register", "payload": {"id": "payload-1", "name": "camera", "base_url": "http://payload.local", "capabilities": ["vision.detect"]}},
        {"type": "payload.get", "payload": {"id": "payload-1"}},
        {"type": "payload.heartbeat", "payload": {"id": "payload-1"}},
        {"type": "payload.list", "payload": {}},
        {"type": "payload.list_by_capability", "payload": {"capability": "vision.detect"}},
        {"type": "payload.route_request", "payload": {"capability": "vision.detect", "request": {"frame": 1}}},
        {"type": "payload.status", "payload": {}},
        {"type": "payload.unregister", "payload": {"id": "payload-1"}},
    ],
    "sweetie-plugin-perception-core": [
        {"type": "perception.ingest", "payload": {"source": "camera", "detections": [{"label": "person", "id": "track-1", "confidence": 0.9, "position": {"x": 1.0, "y": 0.5}}]}},
        {"type": "perception.track_list", "payload": {}},
        {"type": "perception.status", "payload": {}},
        {"type": "perception.reset", "payload": {}},
    ],
    "sweetie-plugin-runtime-orchestrator": [
        {"type": "runtime.register_routes", "payload": {"world_model_url": "http://world", "nav_url": "http://nav", "mission_url": "http://mission", "sim_url": "http://sim"}},
        {"type": "runtime.follow_object", "payload": {"object_id": "obj-1", "standoff_m": 1.0}},
        {"type": "runtime.patrol_mission", "payload": {"waypoints": [{"x": 0.0, "y": 0.0}, {"x": 2.0, "y": 2.0}], "loop": False}},
        {"type": "runtime.simulate_chain", "payload": {"episode_name": "smoke", "steps": [{"observation": {"see": "human"}, "action": {"type": "wave"}, "reward": 1.0, "done": True}] }},
        {"type": "runtime.status", "payload": {}},
    ],
    "sweetie-plugin-safety-governor": [
        {"type": "safety.evaluate_action", "payload": {"action": {"type": "robot.command", "speed": 0.2}, "context": {"battery_percent": 0.9, "human_distance_m": 2.0}}},
        {"type": "safety.set_policy", "payload": {"max_speed_mps": 0.4, "min_human_distance_m": 0.8}},
        {"type": "safety.get_policy", "payload": {}},
        {"type": "safety.report_context", "payload": {"context": {"battery": 0.7}}},
        {"type": "safety.estop", "payload": {}},
        {"type": "safety.clear_estop", "payload": {}},
        {"type": "safety.status", "payload": {}},
    ],
    "sweetie-plugin-sim-learn": [
        {"type": "sim.episode_start", "payload": {"episode_name": "test-episode", "scenario": "smoke"}},
        {"type": "sim.dataset_list", "payload": {}},
        {"type": "sim.status", "payload": {}},
    ],
    "sweetie-plugin-unitree-compat": [
        {"type": "robot.command", "payload": {"action": "move", "direction": "forward", "speed": 0.2}},
        {"type": "robot.posture", "payload": {"preset": "sit"}},
        {"type": "robot.motion_preset", "payload": {"preset": "patrol_step"}},
        {"type": "robot.sequence", "payload": {"commands": [{"action": "move", "direction": "left", "speed": 0.1}]}},
    ],
    "sweetie-plugin-world-model": [
        {"type": "world.upsert_object", "payload": {"id": "obj-1", "label": "human", "position": {"x": 1.0, "y": 2.0, "z": 0.0}}},
        {"type": "world.get_object", "payload": {"id": "obj-1"}},
        {"type": "world.observe", "payload": {"source": "camera", "objects": [{"id": "obj-2", "label": "chair", "position": {"x": 3.0, "y": 4.0, "z": 0.0}}]}},
        {"type": "world.list_objects", "payload": {}},
        {"type": "world.query_near", "payload": {"origin": {"x": 0.0, "y": 0.0, "z": 0.0}, "radius_m": 10.0}},
        {"type": "world.status", "payload": {}},
        {"type": "world.delete_object", "payload": {"id": "obj-1"}},
        {"type": "world.clear", "payload": {}},
    ],
}


UNKNOWN_ACTION_CASE = {"type": "__definitely_unknown__", "payload": {"probe": True}}
MALFORMED_CASE = {"payload": {"missing": "type"}}
