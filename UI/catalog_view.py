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

    concepts = catalog.get("concepts", [])
    subdomains = catalog.get("subdomains", [])

    tab_overview, tab_concepts, tab_export = st.tabs(
        ["📊 Visão Geral", "📚 Conceitos", "⬇️ Exportar"]
    )

    # =========================
    # VISÃO GERAL
    # =========================
    with tab_overview:
        st.metric("Conceitos", len(concepts))
        st.metric("Subdomínios", len(subdomains))

    # =========================
    # CONCEITOS
    # =========================
    with tab_concepts:
        if not concepts:
            st.warning("Nenhum conceito encontrado.")
            return

        df = pd.DataFrame(concepts)
        st.dataframe(df, use_container_width=True)

    # =========================
    # EXPORTAÇÃO
    # =========================
    with tab_export:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                "📄 JSON",
                data=export_catalog_to_json(catalog),
                file_name="catalogo.json",
                mime="application/json"
            )

        with col2:
            st.download_button(
                "📊 CSV",
                data=export_concepts_to_csv(concepts),
                file_name="conceitos.csv",
                mime="text/csv"
            )

        with col3:
            st.download_button(
                "📝 Markdown",
                data=export_catalog_to_markdown(catalog),
                file_name="catalogo.md",
                mime="text/markdown"
            )
