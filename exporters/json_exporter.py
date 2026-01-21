import json

def export_catalog_to_json(catalog: dict) -> str:
    return json.dumps(catalog, indent=2, ensure_ascii=False)
