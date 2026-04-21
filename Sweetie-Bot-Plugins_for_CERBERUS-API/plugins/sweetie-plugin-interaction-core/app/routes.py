from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models import ProcessEventRequest
from app.services.state import state
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

    if t in {"interaction.process_event","interaction.decide_engagement","interaction.suggest_response"}:
        m = ProcessEventRequest(**req.payload)
        event = m.event
        payload = event.get("payload", {}) or {}
        tags = payload.get("tags", []) or []
        target_id = payload.get("track_id")
        state.engagement_target = target_id

        bonding_rank = None
        if target_id:
            bonding_rank = await call_execute(settings.bonding_url, {
                "type":"bonding.rank_attention",
                "payload":{"visible_human_ids":[target_id]}
            })

        # choose interaction intent
        intent = "observe_person"
        if "operator" in tags:
            state.last_action = "follow_operator"
            intent = "engage_operator"
        elif payload.get("label") == "person":
            state.last_action = "observe_person"

        behavior = await call_execute(settings.behavior_url, {
            "type":"behavior.process_intent",
            "payload":{"intent": intent, "context":{"target_id": target_id, "is_operator":"operator" in tags}}
        })

        speech_text = (((behavior or {}).get("data") or {}).get("speech"))
        tts = None
        if speech_text:
            tts = await call_execute(settings.tts_url, {
                "type":"tts.speak",
                "payload":{
                    "text": speech_text,
                    "tone": (((behavior or {}).get("data") or {}).get("tone","warm_playful")),
                    "emotion": (((behavior or {}).get("data") or {}).get("mood","neutral")),
                }
            })

        result = {
            "engagement_target": target_id,
            "intent": intent,
            "behavior": behavior,
            "tts": tts,
            "bonding_rank": bonding_rank,
        }
        state.recent_interactions.append(result)
        state.recent_interactions = state.recent_interactions[-20:]
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=result).model_dump()

    if t == "interaction.get_state":
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data=state.__dict__).model_dump()

    if t == "interaction.reset":
        state.engagement_target = None
        state.last_action = None
        state.recent_interactions.clear()
        return PluginResponse(plugin=settings.plugin_name, action=req.type, data={"reset":True}).model_dump()

    raise HTTPException(status_code=400, detail=f"Unsupported action type: {req.type}")
