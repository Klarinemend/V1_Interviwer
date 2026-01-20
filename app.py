import streamlit as st
import time

from infra.gemini_client import get_random_client
from core.chat_engine import ChatEngine
from core.history import ConversationRepository
from core.extraction.concept_extractor import ConceptExtractor
from core.clustering.subdomain_detector import SubdomainDetector
from UI import render_sidebar, render_chat



# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Engenheiro de Requisitos",
    layout="wide"
)


# ==============================================================================
# CLIENT FACTORY
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
"""


# ==============================================================================
# INICIALIZAÇÃO DOS COMPONENTES
# ==============================================================================
chat_engine = ChatEngine(
    model=MODEL_NAME,
    system_instruction=SYSTEM_INSTRUCTION,
    client_factory=client_factory
)

conversation_repo = ConversationRepository("historico_conversas")

concept_extractor = ConceptExtractor(
    gemini_client=client_factory()
)

subdomain_detector = SubdomainDetector(
    gemini_client=client_factory()
)


# ==============================================================================
# SESSION STATE
# ==============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []


# ==============================================================================
# USER INPUT
# ==============================================================================
def on_new_chat():
    st.session_state.messages = []
    st.rerun()


def on_analyze_domain():
    concepts = concept_extractor.extract_from_messages(
        st.session_state.messages,
        use_ai_enrichment=True
    )

    subdomains = subdomain_detector.detect(
        concepts,
        use_ai_naming=True
    )

    st.success("Análise concluída!")
    st.json(subdomains)


render_sidebar(
    conversation_repo=conversation_repo,
    on_new_chat=on_new_chat,
    on_analyze_domain=on_analyze_domain
)

render_chat(chat_engine)

