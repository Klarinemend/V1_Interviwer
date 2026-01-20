import random
from google import genai
import streamlit as st

def get_random_client():
    api_keys = st.secrets["apiKeys"]
    if not api_keys:
        raise RuntimeError("Nenhuma API Key configurada")
    return genai.Client(api_key=random.choice(api_keys))
