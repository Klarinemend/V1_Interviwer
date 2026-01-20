"""
Pacote de interface (Streamlit UI).
Responsável apenas por renderização e interação com o usuário.
"""

from .sidebar import render_sidebar
from .chat_view import render_chat

__all__ = [
    "render_sidebar",
    "render_chat",
]
