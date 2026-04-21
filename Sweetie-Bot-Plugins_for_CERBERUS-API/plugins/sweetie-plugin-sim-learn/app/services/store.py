from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, UTC
from typing import Dict

from app.config import settings

def now_iso() -> str:
    return datetime.now(UTC).isoformat()

class SimStore:
    def __init__(self):
        self.episodes: Dict[str, dict] = {}
        self.replays: Dict[str, dict] = {}
        os.makedirs(settings.default_dataset_dir, exist_ok=True)

    def episode_start(self, episode_name: str, scenario: str, metadata: dict) -> dict:
        episode_id = str(uuid.uuid4())
        episode = {
            "episode_id": episode_id,
            "episode_name": episode_name,
            "scenario": scenario,
            "metadata": metadata,
            "status": "active",
            "started_at": now_iso(),
            "ended_at": None,
            "outcome": None,
            "summary": {},
            "steps": [],
        }
        self.episodes[episode_id] = episode
        return episode

    def step(self, episode_id: str, observation: dict, action: dict, reward: float, done: bool, notes: list[str]) -> dict | None:
        episode = self.episodes.get(episode_id)
        if not episode:
            return None
        step_index = len(episode["steps"])
        step = {
            "step_index": step_index,
            "timestamp": now_iso(),
            "observation": observation,
            "action": action,
            "reward": reward,
            "done": done,
            "notes": notes,
        }
        episode["steps"].append(step)
        if done:
            episode["status"] = "done"
        return step

    def episode_end(self, episode_id: str, outcome: str, summary: dict) -> dict | None:
        episode = self.episodes.get(episode_id)
        if not episode:
            return None
        episode["status"] = "ended"
        episode["ended_at"] = now_iso()
        episode["outcome"] = outcome
        episode["summary"] = summary
        self._write_dataset(episode)
        return episode

    def replay_create(self, episode_id: str) -> dict | None:
        episode = self.episodes.get(episode_id)
        if not episode:
            return None
        replay_id = str(uuid.uuid4())
        replay = {
            "replay_id": replay_id,
            "episode_id": episode_id,
            "created_at": now_iso(),
            "timeline": episode["steps"],
            "summary": {
                "episode_name": episode["episode_name"],
                "scenario": episode["scenario"],
                "step_count": len(episode["steps"]),
                "outcome": episode["outcome"],
            },
        }
        self.replays[replay_id] = replay
        return replay

    def replay_get(self, replay_id: str) -> dict | None:
        return self.replays.get(replay_id)

    def dataset_list(self) -> list[dict]:
        results = []
        for name in sorted(os.listdir(settings.default_dataset_dir)):
            if not name.endswith(".json"):
                continue
            full = os.path.join(settings.default_dataset_dir, name)
            results.append({
                "file": name,
                "path": full,
                "size_bytes": os.path.getsize(full),
            })
        return results

    def dataset_export(self, episode_id: str | None = None) -> dict:
        if episode_id:
            episode = self.episodes.get(episode_id)
            if not episode:
                return {"results": []}
            path = self._dataset_path(episode["episode_id"])
            if not os.path.exists(path):
                self._write_dataset(episode)
            return {"results": [self._file_info(path)]}
        return {"results": self.dataset_list()}

    def status(self) -> dict:
        active = [e for e in self.episodes.values() if e["status"] == "active"]
        return {
            "episode_count": len(self.episodes),
            "active_episode_count": len(active),
            "replay_count": len(self.replays),
            "dataset_dir": settings.default_dataset_dir,
        }

    def _dataset_path(self, episode_id: str) -> str:
        return os.path.join(settings.default_dataset_dir, f"{episode_id}.json")

    def _write_dataset(self, episode: dict) -> str:
        path = self._dataset_path(episode["episode_id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(episode, f, indent=2)
        return path

    def _file_info(self, path: str) -> dict:
        return {
            "file": os.path.basename(path),
            "path": path,
            "size_bytes": os.path.getsize(path),
        }

store = SimStore()
