def build_framework_structure(framework_name, components):
    structure = {
        "type": "framework_overview",
        "framework": framework_name,
        "components": []
    }

    for c in components:
        structure["components"].append({
            "name": c["name"],
            "description": ""  # filled by LLM later
        })

    return structure

def build_structured_context(graph_context, vector_results):
    sections = {}

    sections["concepts"] = [
        e["name"] for e in graph_context.get("entities", [])
    ]

    sections["relationships"] = [
        f"{r['from']} {r['type']} {r['to']}"
        for r in graph_context.get("relationships", [])
    ]

    sections["documents"] = [
        v["chunk"]["text"][:500]
        for v in vector_results
    ]

    return sections