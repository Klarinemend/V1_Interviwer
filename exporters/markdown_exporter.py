def export_catalog_to_markdown(catalog: dict) -> str:
    md = ["# 📚 Catálogo de Conhecimento\n"]

    md.append("## 🔑 Conceitos\n")
    for c in catalog.get("concepts", []):
        md.append(f"### {c['concept']}")
        md.append(f"- Frequência: {c['frequency']}")
        if c.get("examples"):
            md.append("- Exemplos:")
            for ex in c["examples"]:
                md.append(f"  - {ex}")
        md.append("")

    md.append("## 🧩 Subdomínios\n")
    for s in catalog.get("subdomains", []):
        md.append(f"### {s['name']}")
        for c in s.get("concepts", []):
            md.append(f"- {c}")
        md.append("")

    return "\n".join(md)
