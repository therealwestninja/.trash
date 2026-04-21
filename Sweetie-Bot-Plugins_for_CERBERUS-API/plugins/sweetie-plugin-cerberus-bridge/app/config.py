from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    plugin_name: str
    plugin_version: str
    plugin_port: int


def load_settings(default_name: str, default_version: str, default_port: int) -> Settings:
    return Settings(
        plugin_name=os.getenv("PLUGIN_NAME", default_name),
        plugin_version=os.getenv("PLUGIN_VERSION", default_version),
        plugin_port=int(os.getenv("PLUGIN_PORT", str(default_port))),
    )

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BridgeSettings(Settings):
    cerberus_base_url: str
    cerberus_api_key: str
    request_timeout_s: float


def get_settings() -> BridgeSettings:
    base = load_settings("sweetie-plugin-cerberus-bridge", "1.0.0", 7010)
    return BridgeSettings(
        **base.__dict__,
        cerberus_base_url=os.getenv("CERBERUS_BASE_URL", "http://localhost:8000").rstrip("/"),
        cerberus_api_key=os.getenv("CERBERUS_API_KEY", ""),
        request_timeout_s=float(os.getenv("CERBERUS_REQUEST_TIMEOUT_S", "10")),
    )
