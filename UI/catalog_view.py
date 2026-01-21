import streamlit as st
import pandas as pd

from exporters.json_exporter import export_catalog_to_json
from exporters.csv_exporter import export_concepts_to_csv
from exporters.markdown_exporter import export_catalog_to_markdown


def render_catalog_view():
    catalog = st.session_state.get("catalog")

    if not catalog:
        st.info("Nenhum catálogo gerado ainda.")
        return

    st.subheader("📊 Visão Geral")
    st.metric("Conceitos", len(catalog["concepts"]))
    st.metric("Subdomínios", len(catalog["subdomains"]))

    st.divider()

    st.subheader("📚 Conceitos")
    df = pd.DataFrame(catalog["concepts"])
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("⬇️ Exportar")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "📄 JSON",
            export_catalog_to_json(catalog),
            "catalogo.json",
            "application/json"
        )

    with col2:
        st.download_button(
            "📊 CSV",
            export_concepts_to_csv(catalog["concepts"]),
            "conceitos.csv",
            "text/csv"
        )

    with col3:
        st.download_button(
            "📝 Markdown",
            export_catalog_to_markdown(catalog),
            "catalogo.md",
            "text/markdown"
        )
