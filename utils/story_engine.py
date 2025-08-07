import os
import json
import glob
from typing import Dict, List


class StorySessionManager:
    """Manage user-specific story sessions with persistent state."""

    def __init__(self, chapters_dir: str = "chapters", session_dir: str = os.path.join("data", "sessions")):
        self.chapters_dir = chapters_dir
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)
        self.chapters = sorted(glob.glob(os.path.join(self.chapters_dir, "*.md")))

    # Helper to build response
    def _build_response(self, state: Dict) -> Dict:
        idx = state.get("index", 0)
        if idx < len(self.chapters):
            with open(self.chapters[idx], "r", encoding="utf-8") as f:
                text = f.read().strip()
            choices = ["Continue"]
        else:
            text = "*** End of story ***"
            choices = []
        return {"chapter": idx + 1, "text": text, "choices": choices}

    def load_state(self, user_id: str) -> Dict:
        path = os.path.join(self.session_dir, f"{user_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"index": 0, "choices": []}

    def save_state(self, user_id: str, state: Dict) -> None:
        os.makedirs(self.session_dir, exist_ok=True)
        path = os.path.join(self.session_dir, f"{user_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def start_session(self, user_id: str) -> Dict:
        state = {"index": 0, "choices": []}
        self.save_state(user_id, state)
        return self._build_response(state)

    def add_choice(self, user_id: str, choice: str) -> Dict:
        state = self.load_state(user_id)
        state.setdefault("choices", []).append(choice)
        state["index"] = state.get("index", 0) + 1
        self.save_state(user_id, state)
        return self._build_response(state)

    def get_next_chapter(self, user_id: str) -> Dict:
        state = self.load_state(user_id)
        return self._build_response(state)
