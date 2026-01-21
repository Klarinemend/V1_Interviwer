import json
import os


class ConversationCatalogRepository:
    """
    Responsável por persistir o catálogo gerado
    a partir de uma conversa específica.
    """

    def __init__(self, base_path="catalogos"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save(self, catalog: dict, conversation_file: str):
        """
        Salva o catálogo associado a uma conversa.
        """
        filename = conversation_file.replace(".json", ".catalog.json")
        path = os.path.join(self.base_path, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

    def load(self, conversation_file: str):
        """
        Carrega o catálogo associado a uma conversa.
        """
        filename = conversation_file.replace(".json", ".catalog.json")
        path = os.path.join(self.base_path, filename)

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
