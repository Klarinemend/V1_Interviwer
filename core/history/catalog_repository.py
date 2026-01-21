import json
import os
from datetime import datetime


class CatalogRepository:
    def __init__(self, base_path: str = "catalogs"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _build_path(self, conversation_filename: str) -> str:
        name = conversation_filename.replace(".json", "")
        return os.path.join(self.base_path, f"{name}_catalog.json")

    def save(self, catalog: dict, conversation_filename: str):
        path = self._build_path(conversation_filename)

        payload = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "conversation": conversation_filename
            },
            "catalog": catalog
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return os.path.basename(path)

    def load(self, conversation_filename: str):
        path = self._build_path(conversation_filename)

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["catalog"]

    def delete(self, conversation_filename: str):
        path = self._build_path(conversation_filename)

        if os.path.exists(path):
            os.remove(path)
            return True

        return False
