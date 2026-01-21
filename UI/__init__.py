"""
Pacote de interface (Streamlit UI).
Responsável apenas por renderização e interação com o usuário.
"""

from .sidebar import render_sidebar
from .chat_view import render_chat
from .catalog_view import render_catalog_view

__all__ = [
    "render_sidebar",
    "render_chat",
    "render_catalog_view",
]
