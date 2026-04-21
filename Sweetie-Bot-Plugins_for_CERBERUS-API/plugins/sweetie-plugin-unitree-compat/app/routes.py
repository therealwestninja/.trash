from __future__ import annotations
from fastapi import APIRouter
from sweetie_plugin_sdk.models import ExecuteRequest, ExecuteResponse, HealthResponse, PluginManifest
from .models import TranslateRequest
from .translator import MOTION_PRESETS, POSTURE_PRESETS, translate_command
from .cerberus_client import forward_command

router = APIRouter()

MANIFEST = PluginManifest(
    name="sweetie-plugin-unitree-compat",
    version="0.1.0",
    api_version="1",
    description="Unitree-compatible motion adapter for CERBERUS controller and API workflows.",
    capabilities=["robot.command", "robot.sequence", "robot.posture", "robot.motion_preset"],
    entrypoints={"health": "/health", "manifest": "/manifest", "execute": "/execute", "translate": "/translate"},
)

@router.get('/health')
def health() -> HealthResponse:
    return HealthResponse(status='ok', plugin=MANIFEST.name, version=MANIFEST.version)

@router.get('/manifest')
def manifest() -> PluginManifest:
    return MANIFEST

@router.post('/translate')
def translate(req: TranslateRequest):
    return {
        'ok': True,
        'plugin': MANIFEST.name,
        'translated': translate_command(req.model_dump()),
    }

@router.post('/execute')
def execute(req: ExecuteRequest) -> ExecuteResponse:
    warnings = []
    forward = bool(req.context.get('forward_to_cerberus', False))

    if req.type == 'robot.command':
        translated = translate_command(req.payload)
        if translated.get('warning'):
            warnings.append(translated['warning'])
        data = {'normalized_command': req.payload, 'translated_command': translated}
        if forward:
            data['forward_result'] = forward_command(translated)
        return ExecuteResponse(plugin=MANIFEST.name, action=req.type, data=data, warnings=warnings)

    if req.type == 'robot.posture':
        preset = (req.payload.get('preset') or 'neutral').lower()
        command = POSTURE_PRESETS.get(preset, POSTURE_PRESETS['neutral'])
        data = {'preset': preset, 'normalized_command': command, 'translated_command': translate_command(command)}
        if preset not in POSTURE_PRESETS:
            warnings.append(f'Unknown posture preset {preset!r}; neutral used instead.')
        return ExecuteResponse(plugin=MANIFEST.name, action=req.type, data=data, warnings=warnings)

    if req.type == 'robot.motion_preset':
        preset = (req.payload.get('preset') or 'patrol_step').lower()
        sequence = MOTION_PRESETS.get(preset, MOTION_PRESETS['patrol_step'])
        data = {'preset': preset, 'sequence': [{'normalized_command': cmd, 'translated_command': translate_command(cmd)} for cmd in sequence]}
        if preset not in MOTION_PRESETS:
            warnings.append(f'Unknown motion preset {preset!r}; patrol_step used instead.')
        return ExecuteResponse(plugin=MANIFEST.name, action=req.type, data=data, warnings=warnings)

    if req.type == 'robot.sequence':
        commands = req.payload.get('commands', [])
        sequence = []
        for cmd in commands:
            translated = translate_command(cmd)
            if translated.get('warning'):
                warnings.append(translated['warning'])
            sequence.append({'normalized_command': cmd, 'translated_command': translated})
        data = {'sequence': sequence}
        if forward:
            data['forward_results'] = [forward_command(item['translated_command']) for item in sequence]
        return ExecuteResponse(plugin=MANIFEST.name, action=req.type, data=data, warnings=warnings)

    return ExecuteResponse(ok=False, plugin=MANIFEST.name, action=req.type, data={'error': f'Unsupported action type: {req.type}'}, warnings=warnings)
