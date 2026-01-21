import os
import json
from datetime import datetime
from typing import List, Dict


class ConversationRepository:
    """
    Responsável por persistir e recuperar históricos de conversa.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    # =========================
    # SALVAR
    # =========================
    def save(self, messages: List[Dict]) -> str:
        if not messages:
            raise ValueError("Não há mensagens para salvar.")

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        path = os.path.join(self.base_path, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        return filename
    

    # =========================
    # CARREGAR
    # =========================
    def load(self, filename: str) -> List[Dict]:
        path = os.path.join(self.base_path, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo não encontrado: {filename}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # =========================
    # LISTAR
    # =========================
    def list_conversations(self) -> List[str]:
        files = [
            f for f in os.listdir(self.base_path)
            if f.endswith(".json")
        ]
        files.sort(reverse=True)
        return files

    # =========================
    # EXCLUIR
    # =========================
    def delete(self, filename: str) -> None:
        path = os.path.join(self.base_path, filename)

        if os.path.exists(path):
            os.remove(path)
