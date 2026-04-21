from app.state import state

def decide(event):
    topic = event.get("topic","")
    payload = event.get("payload",{})
    tags = payload.get("tags",[])

    if "operator" in tags:
        state.engagement_target = payload.get("track_id")
        state.last_action = "greet_operator"
        return {
            "intent": "engage_operator",
            "action": "follow_operator",
            "speech": "Hello! Following you."
        }

    if topic.startswith("vision.person"):
        state.engagement_target = payload.get("track_id")
        state.last_action = "observe_person"
        return {
            "intent": "observe",
            "action": "observe_person",
            "speech": "I see someone nearby."
        }

    return {
        "intent": "idle",
        "action": "idle_scan",
        "speech": None
    }
