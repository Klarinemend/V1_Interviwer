import streamlit as st
from google import genai
from google.genai import types
import os
import json
import time 
import random
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Engenheiro de Requisitos", layout="wide")

# ==============================================================================
# 🔐 ÁREA DAS CHAVES DE API (Key Rotation)
# ==============================================================================

# Tenta carregar as chaves do arquivo secreto (.streamlit/secrets.toml)
try:
    api_keys_list = st.secrets["apiKeys"]
except FileNotFoundError:
    st.error("Arquivo .streamlit/secrets.toml não encontrado!")
    st.stop()
except KeyError:
    st.error("A lista 'apiKeys' não foi encontrada dentro do secrets.toml")
    st.stop()

# Função de sorteio (continua igual)
def get_random_client():
    if not api_keys_list: return None
    selected_key = random.choice(api_keys_list)
    return genai.Client(api_key=selected_key)

# ==============================================================================
# ==============================================================================

MODEL_NAME = "gemini-2.5-flash" # Modelo rápido e com contexto gigante
PASTA_HISTORICO = "historico_conversas"
os.makedirs(PASTA_HISTORICO, exist_ok=True)

SYSTEM_INSTRUCTION = """
Você é um Engenheiro de Conhecimento Sênior e consultor em Ontologias.
Seu objetivo é entrevistar o usuário para modelar um domínio.
1. Seja polido, curioso e profissional.
2. Use "Escuta Ativa".
3. Se o usuário pedir um RELATÓRIO, gere um documento Markdown completo com todas as especificações coletadas.
"""

# --- FUNÇÕES DE ARQUIVO ---
def salvar_conversa(messages_list):
    if not messages_list:
        st.warning("Nada para salvar.")
        return
    nome_arquivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    caminho = os.path.join(PASTA_HISTORICO, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(messages_list, f, ensure_ascii=False, indent=4)
    st.sidebar.success(f"Salvo: {nome_arquivo}")

def carregar_conversa(nome_arquivo):
    caminho = os.path.join(PASTA_HISTORICO, nome_arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def listar_conversas_salvas():
    try:
        arquivos = [f for f in os.listdir(PASTA_HISTORICO) if f.endswith('.json')]
        arquivos.sort(reverse=True)
        return arquivos
    except:
        return []

# --- ESTADO (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "timestamps_msgs" not in st.session_state:
    st.session_state.timestamps_msgs = []

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("📂 Menu")
    
    if st.button("➕ Nova Conversa", use_container_width=True):
        st.session_state.messages = [] 
        st.session_state.timestamps_msgs = [] 
        st.rerun()

    if st.button("💾 Salvar Histórico", use_container_width=True):
        salvar_conversa(st.session_state.messages)
        st.rerun()
       
    st.subheader("Histórico Salvo")
    arquivos_disponiveis = listar_conversas_salvas()
    
    if arquivos_disponiveis:
        # Caixa de seleção
        arquivo_selecionado = st.selectbox("Selecione o arquivo:", arquivos_disponiveis)
        
        # Cria duas colunas para os botões ficarem lado a lado
        col_carregar, col_deletar = st.columns(2)
        
        # Botão CARREGAR
        with col_carregar:
            if st.button("📂 Abrir", use_container_width=True):
                historico_recuperado = carregar_conversa(arquivo_selecionado)
                if historico_recuperado:
                    st.session_state.messages = historico_recuperado
                    st.session_state.timestamps_msgs = []
                    st.success("Carregado!")
                    time.sleep(0.5) # Dá tempo de ler a mensagem
                    st.rerun()

        # Botão DELETAR
        with col_deletar:
            # type="primary" deixa o botão com destaque (geralmente vermelho/colorido dependendo do tema)
            if st.button("🗑️ Excluir", type="primary", use_container_width=True):
                caminho_completo = os.path.join(PASTA_HISTORICO, arquivo_selecionado)
                try:
                    os.remove(caminho_completo)
                    st.toast(f"Arquivo deletado: {arquivo_selecionado}")
                    time.sleep(0.5)
                    st.rerun() # Recarrega a página para atualizar a lista
                except Exception as e:
                    st.error(f"Erro ao deletar: {e}")

    else:
        st.caption("Nenhuma conversa salva ainda.")


# --- CHAT PRINCIPAL ---
st.title("🤖 Engenheiro de Requisitos")
st.caption("Sou um consultor especializado, irei te entrevistar para entender e modelar as regras do seu sistema/domínio.\n Poderia me falar sobre ele?")

# Exibe todo o histórico visualmente
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "assistant"
    avatar = "🧑‍💻" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# --- LÓGICA DE ENVIO ---
prompt = st.chat_input("Digite aqui...")

if prompt:
    # 1. Mostra e salva a mensagem do usuário
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Processamento da IA
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        placeholder.markdown("Pensando...")
        
        try:
            # === LÓGICA INTELIGENTE DE CONTEXTO ===
            
            # Detecta se é um pedido de relatório final
            termos_relatorio = ["gerar relatorio", "gerar relatório", "relatório final", "resumo completo", "documentação"]
            eh_relatorio = any(t in prompt.lower() for t in termos_relatorio)
            
            msgs_para_contexto = []
            
            if eh_relatorio:
                # MODO RELATÓRIO: Envia TUDO (Histórico Completo)
                # O Gemini Flash tem 1 milhão de tokens, aguenta ler tudo de uma vez.
                st.toast("📄 Detectado pedido de relatório: Lendo histórico completo...", icon="🧠")
                msgs_para_contexto = st.session_state.messages[:-1] # Tudo até antes do prompt atual
            else:
                # MODO CONVERSA: Janela Deslizante (Últimas 10 mensagens)
                # Mantém o custo baixo e a velocidade alta.
                JANELA = 10
                if len(st.session_state.messages) > JANELA:
                    msgs_para_contexto = st.session_state.messages[-(JANELA+1):-1]
                else:
                    msgs_para_contexto = st.session_state.messages[:-1]
            
            # Converte para formato da API
            api_history = []
            for msg in msgs_para_contexto:
                r = "user" if msg["role"] == "user" else "model"
                api_history.append(types.Content(
                    role=r,
                    parts=[types.Part(text=msg["content"])]      
                ))
            
            # === ROTAÇÃO DE CHAVES E ENVIO ===
            client = get_random_client()
            if not client:
                raise Exception("Configure as chaves de API no código!")

            # Cria chat temporário configurado com o histórico escolhido
            chat = client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7
                ),
                history=api_history
            )
            
            # Envia a mensagem atual
            response = chat.send_message(prompt)
            texto = response.text
            
            # Exibe e salva
            placeholder.markdown(texto)
            st.session_state.messages.append({"role": "model", "content": texto})
            
            # Atualiza contador de RPM
            st.session_state.timestamps_msgs.append(time.time())
            time.sleep(0.1) # Pequena pausa para estabilidade
            st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")
