import streamlit as st
import os
import json
import time
from datetime import datetime

from infra.gemini_client import get_random_client
from core.chat_engine import ChatEngine
from core.sabiox_extractor import SabioxExtractor

# ==============================================================================
# CONFIGURAÇÃO INICIAL
# ==============================================================================
st.set_page_config(
    page_title="Engenheiro de Requisitos",
    layout="wide"
)

# ==============================================================================
# CHAVES DE API (Streamlit Secrets)
# ==============================================================================
try:
    api_keys_list = st.secrets["apiKeys"]
except FileNotFoundError:
    st.error("Arquivo .streamlit/secrets.toml não encontrado!")
    st.stop()
except KeyError:
    st.error("A lista 'apiKeys' não foi encontrada dentro do secrets.toml")
    st.stop()


# ==============================================================================
# CLIENT FACTORY (ponte entre Streamlit e infra)
# ==============================================================================
def client_factory():
    return get_random_client()



# ==============================================================================
# CONFIGURAÇÕES DO MODELO
# ==============================================================================
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
Você é um Engenheiro de Conhecimento Sênior e consultor em Ontologias.
Seu objetivo é entrevistar o usuário para modelar um domínio.

1. Seja polido, curioso e profissional.
2. Use escuta ativa.
3. Se o usuário pedir um RELATÓRIO, gere um documento Markdown completo
   com todas as especificações coletadas.
"""


# ==============================================================================
# INICIALIZAÇÃO DO CHAT ENGINE E SABiOx EXTRACTOR
# ==============================================================================
chat_engine = ChatEngine(
    model=MODEL_NAME,
    system_instruction=SYSTEM_INSTRUCTION,
    client_factory=client_factory
)

sabiox_extractor = SabioxExtractor()

# ==============================================================================
# PERSISTÊNCIA DE HISTÓRICO
# ==============================================================================
PASTA_HISTORICO = "historico_conversas"
os.makedirs(PASTA_HISTORICO, exist_ok=True)


def salvar_conversa(messages):
    if not messages:
        st.warning("Nada para salvar.")
        return

    nome_arquivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    caminho = os.path.join(PASTA_HISTORICO, nome_arquivo)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

    st.sidebar.success(f"Salvo: {nome_arquivo}")


def carregar_conversa(nome_arquivo):
    caminho = os.path.join(PASTA_HISTORICO, nome_arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def listar_conversas_salvas():
    try:
        arquivos = [
            f for f in os.listdir(PASTA_HISTORICO)
            if f.endswith(".json")
        ]
        arquivos.sort(reverse=True)
        return arquivos
    except Exception:
        return []


# ==============================================================================
# SESSION STATE
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "timestamps_msgs" not in st.session_state:
    st.session_state.timestamps_msgs = []


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.title("📂 Menu")

    if st.button("➕ Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.timestamps_msgs = []
        st.rerun()
        
    if st.button("🧠 Gerar SABiOx", use_container_width=True):
        if not st.session_state.messages:
            st.warning("Não há conversa para analisar.")
        else:
            sabiox = sabiox_extractor.extrair(
                st.session_state.messages
            )
            st.session_state.sabiox = sabiox
            st.success("SABiOx gerado com sucesso!")

    if st.button("💾 Salvar Histórico", use_container_width=True):
        salvar_conversa(st.session_state.messages)
        st.rerun()

    st.subheader("Histórico Salvo")
    arquivos = listar_conversas_salvas()

    if arquivos:
        arquivo_sel = st.selectbox(
            "Selecione o arquivo:",
            arquivos
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📂 Abrir", use_container_width=True):
                st.session_state.messages = carregar_conversa(arquivo_sel)
                st.session_state.timestamps_msgs = []
                st.success("Histórico carregado!")
                time.sleep(0.5)
                st.rerun()

        with col2:
            if st.button("🗑️ Excluir", type="primary", use_container_width=True):
                try:
                    os.remove(os.path.join(PASTA_HISTORICO, arquivo_sel))
                    st.toast(f"Arquivo deletado: {arquivo_sel}")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao deletar: {e}")
    else:
        st.caption("Nenhuma conversa salva ainda.")


# ==============================================================================
# CHAT PRINCIPAL
# ==============================================================================
st.title("🤖 Engenheiro de Requisitos")
st.caption(
    "Sou um consultor especializado. "
    "Vou te entrevistar para entender e modelar o domínio do seu sistema."
)

# Exibe histórico
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "assistant"
    avatar = "🧑‍💻" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])


# ==============================================================================
# ENVIO DE MENSAGEM
# ==============================================================================
prompt = st.chat_input("Digite aqui...")

if prompt:
    # Mostra mensagem do usuário
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    # Processamento da IA
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        placeholder.markdown("Pensando...")

        try:
            texto = chat_engine.gerar_resposta(
                st.session_state.messages,
                prompt
            )

            placeholder.markdown(texto)

            st.session_state.messages.append(
                {"role": "model", "content": texto}
            )

            st.session_state.timestamps_msgs.append(time.time())
            time.sleep(0.1)

            st.rerun()

        except Exception as e:
            st.error(str(e))
