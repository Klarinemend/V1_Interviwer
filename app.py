import streamlit as st
import time

from infra.gemini_client import get_random_client
from core.chat_engine import ChatEngine
from core.extraction.concept_extractor import ConceptExtractor
from core.clustering.subdomain_detector import SubdomainDetector
from core.history import ConversationRepository, CatalogRepository
from core.catalog import ConversationCatalogRepository


from UI.sidebar import render_sidebar
from UI.chat_view import render_chat
from UI.catalog_view import render_catalog_view


# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="SABiOx - Engenheiro de Requisitos",
    layout="wide"
)

# ==============================================================================
# SESSION STATE
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "catalog" not in st.session_state:
    st.session_state.catalog = None

if "current_view" not in st.session_state:
    st.session_state.current_view = "chat"

# ==============================================================================
# CLIENT FACTORY
# ==============================================================================
def client_factory():
    return get_random_client()


# ==============================================================================
# CONFIGURAÇÕES DO MODELO
# ==============================================================================
MODEL_NAME = "gemini-2.0-flash"

SYSTEM_INSTRUCTION = """
Você é um Engenheiro de Conhecimento Sênior e consultor em Ontologias.
Seu objetivo é entrevistar o usuário para modelar um domínio.
"""


# ==============================================================================
# COMPONENTES
# ==============================================================================
chat_engine = ChatEngine(
    model=MODEL_NAME,
    system_instruction=SYSTEM_INSTRUCTION,
    client_factory=client_factory
)

conversation_repo = ConversationRepository("historico_conversas")
catalog_repo = CatalogRepository("catalogs")
conversation_catalog_repo = ConversationCatalogRepository()


concept_extractor = ConceptExtractor()
subdomain_detector = SubdomainDetector()


# ==============================================================================
# CALLBACKS
# ==============================================================================
def on_new_chat():
    st.session_state.messages = []
    st.session_state.catalog = None
    st.rerun()


def on_analyze_domain():
    messages = st.session_state.get("messages", [])

    if len(messages) < 4:
        st.warning("Conversa insuficiente para análise.")
        return

    with st.spinner("Analisando domínio..."):
        concepts = concept_extractor.extract_from_messages(
            messages,
            min_frequency=2,
            max_concepts=20,
            use_ai_enrichment=False
        )

        subdomains_result = subdomain_detector.detect(
            concepts,
            use_ai_naming=False
        )

        st.session_state.catalog = {
            "concepts": concepts,
            "subdomains": subdomains_result.get("subdomains", []),
            "metadata": {
                "generated_at": time.time(),
                "source": "conversation",
            }
        }

    st.success("✅ Catálogo gerado com sucesso!")


# ==============================================================================
# UI
# ==============================================================================
render_sidebar(
    conversation_repo=conversation_repo,
    catalog_repo=conversation_catalog_repo,
    on_new_chat=on_new_chat,
    on_analyze_domain=on_analyze_domain
)


# ==============================================================================
# ÁREA PRINCIPAL
# ==============================================================================

if st.session_state.current_view == "catalog":
    st.title("📊 Catálogo do Domínio")
    render_catalog_view()

    if st.button("⬅️ Voltar para o Chat"):
        st.session_state.current_view = "chat"
        st.rerun()

elif st.session_state.current_view == "history":
    st.title("📚 Histórico")
    st.info("Use a sidebar para gerenciar conversas.")

else:
    render_chat(chat_engine)


