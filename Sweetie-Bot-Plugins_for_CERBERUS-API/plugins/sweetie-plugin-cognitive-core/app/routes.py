from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import PerceiveEventRequest, EvaluateContextRequest, ChooseActionRequest, SetStateRequest
from app.services.cognition import interpret_event, evaluate_context, dump_state, set_state_fields, reset_state
from app.services.http_clients import call_execute
from sweetie_plugin_sdk.models import ExecuteRequest, PluginResponse
from sweetie_plugin_sdk.manifest import load_manifest

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok","plugin":settings.plugin_name,"version":settings.plugin_version}

@router.get("/manifest")
def manifest():
    return load_manifest()

@router.post("/execute")
async def execute(req: ExecuteRequest):
    t = req.type.strip().lower()

    if t == "cognition.perceive_event":
        m = PerceiveEventRequest(**req.payload)
        interpreted = interpret_event(m.event.model_dump())
        event = m.event.model_dump()
        payload = event.get("payload", {}) or {}
        tags = payload.get("tags", []) or []
        human_id = payload.get("track_id")

        memory_result = await call_execute(settings.memory_url, {
            "type":"memory.store_episode",
            "payload":{
                "text": f"Observed event {event.get('topic')} with intent {interpreted['intent']}.",
                "tags": tags,
                "source": settings.plugin_name,
                "salience": interpreted["attention_score"],
                "relationship_tier": "best_friend" if "operator" in tags else ("supporting" if "staff" in tags else "public"),
                "metadata": {"event": event}
            }
        })

        bonding_result = None
        if human_id:
            bonding_result = await call_execute(settings.bonding_url, {
                "type":"bonding.observe_human",
                "payload":{
                    "human_id": human_id,
                    "event":"positive_interaction" if "operator" in tags else "neutral_seen",
                    "tags": tags
                }
            })

        attention_result = None
        if human_id:
            attention_result = await call_execute(settings.attention_url, {
                "type":"attention.ingest_candidates",
                "payload":{"candidates":[
                    {
                        "target_id": human_id,
                        "label": payload.get("label","unknown"),
                        "confidence": payload.get("confidence",0.7),
                        "tags": tags,
                        "distance_m": payload.get("distance_m",1.0),
                        "novelty": 0.2 if "operator" in tags else 0.4,
                        "salience": interpreted["attention_score"]
                    }
                ]}
            })

        bus_result = await call_execute(settings.event_bus_url, {
            "type":"event.publish",
            "payload":{"topic":"cognition.event_interpreted","source":settings.plugin_name,"payload":interpreted,"tags":tags}
        })

        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={
            "interpretation": interpreted,
            "memory_result": memory_result,
            "bonding_result": bonding_result,
            "attention_result": attention_result,
            "bus_result": bus_result,
            "state": dump_state(),
        }).model_dump()

    if t == "cognition.evaluate_context":
        m = EvaluateContextRequest(**req.payload)
        autonomy = await call_execute(settings.autonomy_url, {"type":"autonomy.evaluate_mode","payload":m.context})
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={
            "evaluation": evaluate_context(m.context),
            "autonomy_mode": autonomy
        }).model_dump()

    if t == "cognition.choose_action":
        m = ChooseActionRequest(**req.payload)
        ctx = m.context
        auto = await call_execute(settings.autonomy_url, {"type":"autonomy.choose_goal","payload":{"context":ctx}})
        goal_data = ((auto or {}).get("data") or {})
        mode = goal_data.get("mode", "idle")
        goal = goal_data.get("goal", "idle_observe")
        suggested = goal_data.get("suggested_action") or {"type":"action.dispatch","payload":{"action_name":"idle_scan","payload_override":{}}}

        # Behavior shaping
        intent_for_behavior = "idle"
        if mode == "follow_operator":
            intent_for_behavior = "follow_operator"
        elif mode == "social":
            intent_for_behavior = "observe_person"
        elif mode in {"dock_seek","dock_urgent"}:
            intent_for_behavior = "avoid_hazard"
        elif mode == "explore":
            intent_for_behavior = "explore_novel_object"

        behavior = await call_execute(settings.behavior_url, {
            "type":"behavior.process_intent",
            "payload":{"intent": intent_for_behavior, "context": ctx}
        })

        # Safety review
        safety = await call_execute(settings.safety_url, {
            "type":"safety.evaluate_action",
            "payload":{"action": suggested, "context": ctx}
        })

        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={
            "goal": goal,
            "mode": mode,
            "suggested_action": suggested,
            "behavior": behavior,
            "safety": safety,
            "state": dump_state(),
        }).model_dump()

    if t == "cognition.set_state":
        m = SetStateRequest(**req.payload)
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": set_state_fields(m.model_dump())}).model_dump()

    if t == "cognition.get_state":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": dump_state()}).model_dump()

    if t == "cognition.reset":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"state": reset_state()}).model_dump()

    if t == "cognition.status":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=dump_state()).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
