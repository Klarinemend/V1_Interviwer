import streamlit as st


def render_chat(chat_engine):
    st.title("🤖 Engenheiro de Requisitos")

    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        avatar = "🧑‍💻" if role == "user" else "🤖"

        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])

    prompt = st.chat_input("Digite sua mensagem...")

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("assistant", avatar="🤖"):
            response = chat_engine.gerar_resposta(
                st.session_state.messages,
                prompt
            )
            st.markdown(response)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        st.rerun()
    