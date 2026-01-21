import streamlit as st


def render_sidebar(
    conversation_repo,
    catalog_repo,
    on_new_chat,
    on_analyze_domain
):
    with st.sidebar:
        st.title("Engnheiro de Requisitos")
        st.caption("Engenharia de Requisitos com IA")
        st.divider()

        # ==========================================================
        # NAVEGAÇÃO PRINCIPAL
        # ==========================================================
        LABELS = {
            "chat": "💬 Chat",
            "catalog": "📊 Catálogo",
            "history": "📚 Histórico",
        }

        view = st.radio(
            "📂 Navegação",
            options=list(LABELS.keys()),
            format_func=lambda k: LABELS[k],
            index=_get_view_index(),
        )

        st.session_state.current_view = view


        st.divider()

        # ==========================================================
        # AÇÕES CONTEXTUAIS
        # ==========================================================
        if view == "chat":
            render_chat_actions(on_new_chat, on_analyze_domain)

        elif view == "catalog":
            render_catalog_info(on_analyze_domain)

        elif view == "history":
            render_history_actions(conversation_repo, catalog_repo, on_analyze_domain)


# ==============================================================
# CHAT ACTIONS
# ==============================================================

def render_chat_actions(on_new_chat, on_analyze_domain):
    st.subheader("💬 Conversa")

    if st.button("🆕 Nova Conversa", use_container_width=True):
        on_new_chat()

    st.divider()

    num_messages = len(st.session_state.get("messages", []))

    if st.button(
        "🔍 Extrair Conceitos",
        use_container_width=True,
        disabled=num_messages < 4,
        help="Mínimo de 4 mensagens necessárias"
    ):
        with st.spinner("🧠 Analisando domínio..."):
            on_analyze_domain()

    st.caption(f"{num_messages} mensagens na conversa")

    if num_messages < 4:
        st.info("💡 Continue conversando para habilitar a análise")


# ==============================================================
# CATÁLOGO INFO
# ==============================================================

def render_catalog_info(on_analyze_domain):
    st.subheader("📊 Catálogo")

    catalog = st.session_state.get("catalog")

    if not catalog:

        st.info(
            """
📋 **Como funciona**
1. Converse sobre seu domínio
2. Vá para **Chat**
3. Clique em **Extrair Conceitos**
            """
        )
        return

    catalog = st.session_state.get("catalog")

    if catalog:
        st.success("✅ Catálogo disponível")

        st.metric("Conceitos", len(catalog.get("concepts", [])))
        st.metric("Subdomínios", len(catalog.get("subdomains", [])))

    st.divider()

    if st.button(
        "🔄 Regerar Catálogo",
        use_container_width=True,
        help="Reanalisa a conversa atual"
    ):
        with st.spinner("🧠 Reanalisando domínio..."):
            on_analyze_domain()
        st.rerun()

    if catalog and st.button("🗑️ Limpar Catálogo", use_container_width=True):
        st.session_state.catalog = None
        st.rerun()



# ==============================================================
# HISTÓRICO ACTIONS
# ==============================================================

def render_history_actions(conversation_repo, catalog_repo, on_analyze_domain):

    st.subheader("📚 Histórico")

    if st.button("💾 Salvar Conversa Atual", use_container_width=True):
        messages = st.session_state.get("messages")

        if not messages:
            st.warning("Nenhuma mensagem para salvar")
            return

        filename = conversation_repo.save(messages)

        if st.session_state.get("catalog"):
            catalog_repo.save(st.session_state.catalog, filename)

        st.success("✅ Conversa salva")
        st.rerun()

    st.divider()
    
    if st.button("🔍 Extrair Conceitos dessa Conversa", use_container_width=True):
        messages = st.session_state.get("messages")

        if not messages or len(messages) < 4:
            st.warning("Conversa muito curta para análise")
        else:
            with st.spinner("🧠 Reanalisando conversa..."):
                on_analyze_domain()
            st.success("Catálogo atualizado a partir do histórico")
            st.session_state.current_view = "catalog"
            st.rerun()

    st.divider()

    histories = conversation_repo.list_conversations()

    if not histories:
        st.caption("_Nenhuma conversa salva ainda_")
        return

    selected = st.selectbox(
        "Conversas salvas",
        histories,
        format_func=lambda x: x.replace(".json", ""),
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📂 Carregar", use_container_width=True):
            st.session_state.messages = conversation_repo.load(selected)
            st.session_state.catalog = catalog_repo.load(selected)
            st.success("Conversa carregada")
            st.rerun()

    with col2:
        if st.button("🗑️ Excluir", type="primary", use_container_width=True):
            conversation_repo.delete(selected)
            catalog_repo.delete(selected)
            st.toast("Conversa excluída")
            st.rerun()


# ==============================================================
# HELPERS
# ==============================================================

def _get_view_index():
    view = st.session_state.get("current_view", "chat")
    options = ["chat", "catalog", "history"]
    return options.index(view) if view in options else 0
