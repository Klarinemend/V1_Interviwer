import csv
import io

def export_concepts_to_csv(concepts: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["concept", "frequency", "examples"]
    )
    writer.writeheader()

    for c in concepts:
        writer.writerow({
            "concept": c.get("concept"),
            "frequency": c.get("frequency"),
            "examples": "; ".join(c.get("examples", []))
        })

    return output.getvalue()
