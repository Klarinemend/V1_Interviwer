import streamlit as st

def render_sidebar(conversation_repo, on_new_chat, on_analyze_domain):
    with st.sidebar:
        st.title("🧠 SABiOx")

        st.divider()

        if st.button("🆕 Novo chat"):
            on_new_chat()

        st.divider()

        st.subheader("📚 Histórico")

        histories = conversation_repo.list_conversations()

        if not histories:
            st.caption("Nenhuma conversa salva.")

        for conv in histories:
            if st.button(conv, key=f"conv_{conv}"):
                messages = conversation_repo.load(conv)
                st.session_state.messages = messages
                st.rerun()

        st.divider()

        if st.button("🔍 Analisar domínio"):
            on_analyze_domain()
