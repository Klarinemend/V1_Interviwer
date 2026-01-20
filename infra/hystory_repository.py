import os
import json
from datetime import datetime


class HistoryRepository:
    def __init__(self, base_path="historico_conversas"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, messages):
        if not messages:
            return None

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        path = os.path.join(self.base_path, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)

        return filename

    def load(self, filename):
        path = os.path.join(self.base_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def list(self):
        try:
            files = [
                f for f in os.listdir(self.base_path)
                if f.endswith(".json")
            ]
            files.sort(reverse=True)
            return files
        except Exception:
            return []

    def delete(self, filename):
        try:
            os.remove(os.path.join(self.base_path, filename))
            return True
        except Exception:
            return False
