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
class CharacterSettings(Settings):
    sweetie_name: str


def get_settings() -> CharacterSettings:
    base = load_settings("sweetie-plugin-character", "1.0.0", 7011)
    return CharacterSettings(
        **base.__dict__,
        sweetie_name=os.getenv("SWEETIE_NAME", "Sweetie-Bot"),
    )
