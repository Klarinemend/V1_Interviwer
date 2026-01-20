import json
import os
from datetime import datetime
from infra.paths import PASTA_HISTORICO, PASTA_SPECS

def salvar_conversa(messages):
    nome = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    with open(os.path.join(PASTA_HISTORICO, nome), "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    return nome

def carregar_conversa(nome):
    with open(os.path.join(PASTA_HISTORICO, nome), "r", encoding="utf-8") as f:
        return json.load(f)

def listar_conversas():
    return sorted(
        [f for f in os.listdir(PASTA_HISTORICO) if f.endswith(".json")],
        reverse=True
    )
