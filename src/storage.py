import json
from pathlib import Path
from typing import Any, Dict, Optional

from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

class JSONStorage(BaseStorage):
    """
    Простое хранилище FSM, использующее JSON-файл.
    Подходит для локальной разработки и ботов с низкой нагрузкой.
    """
    def __init__(self, path: str):
        self.path = Path(path)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    async def close(self) -> None:
        self._save()

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        user_key = str(key.user_id)
        if user_key not in self.data:
            self.data[user_key] = {}
        
        self.data[user_key]["state"] = state.state if state else None
        self._save()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        user_key = str(key.user_id)
        return self.data.get(user_key, {}).get("state")

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        user_key = str(key.user_id)
        if user_key not in self.data:
            self.data[user_key] = {}
        
        if "data" not in self.data[user_key]:
            self.data[user_key]["data"] = {}
        self.data[user_key]["data"].update(data)
        self._save()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        user_key = str(key.user_id)
        return self.data.get(user_key, {}).get("data", {})
    
    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        user_key = str(key.user_id)
        if user_key not in self.data or "data" not in self.data[user_key]:
            self.data.setdefault(user_key, {})["data"] = data
        else:
            self.data[user_key]["data"].update(data)
        self._save()
        return self.data[user_key]["data"].copy()