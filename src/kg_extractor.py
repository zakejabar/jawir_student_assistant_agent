import json
import re
from typing import List, Dict, Any, Tuple
from config.llm_config import llm_config
from src.neo4j_client import neo4j_client
from src.chunking.semantic_chunker import semantic_chunk


class KnowledgeGraphExtractor:
    def __init__(self):
        self.llm = llm_config.get_llm()

    def extract_entities_relationships(
        self, text_chunk: str, user_id: str
    ) -> Tuple[List[Dict], List[Dict]]:

        extraction_prompt = f"""
You are an academic knowledge graph extractor for university-level learning materials.

Extract ONLY study-relevant knowledge. Ignore:
- Copyright notices
- Slide numbers
- Repeated headings
- URLs
- Decorative text

PRIORITIZE:
1. Core concepts and definitions
2. Frameworks and models
3. Components or steps
4. Learning objectives
5. Case studies and examples
6. Cause–effect or purpose relationships

Text:
\"\"\"{text_chunk}\"\"\"

ENTITY TYPES:
- concept
- framework
- definition
- learning_objective
- organization
- example
- process
- step

RELATIONSHIP TYPES:
- defines
- has_component
- has_step
- part_of
- example_of
- used_in
- supports
- objective_of
- cause_of

RULES:
- Entity names: 2–6 words
- No duplicates
- Canonical academic terms only

Return ONLY valid JSON:
{{
  "entities": [
    {{"name": "Integrated Marketing Communications", "type": "concept"}}
  ],
  "relationships": [
    {{"from": "Promotion Mix", "to": "Advertising", "type": "has_component"}}
  ]
}}
"""

        try:
            response = self.llm.invoke(extraction_prompt)
            content = self._clean_json_response(response.content.strip())
            data = json.loads(content)

            entities = self._clean_entities(data.get("entities", []))
            relationships = self._clean_relationships(data.get("relationships", []))

            return entities, relationships

        except Exception as e:
            print("KG extraction error:", e)
            print("Raw response:", response.content)
            return [], []

    def _clean_json_response(self, content: str) -> str:
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"\s*```", "", content)

        start = content.find("{")
        end = content.rfind("}")

        return content[start:end + 1] if start != -1 and end != -1 else content

    def _clean_entities(self, entities: List[Dict]) -> List[Dict]:
        allowed_types = {
            "concept", "framework", "definition",
            "learning_objective", "organization",
            "example", "process", "step"
        }

        cleaned = []
        seen = set()

        for e in entities:
            if not isinstance(e, dict):
                continue

            name = e.get("name", "").strip()
            etype = e.get("type", "concept").lower().strip()

            if not name or name in seen:
                continue

            if etype not in allowed_types:
                etype = "concept"

            cleaned.append({"name": name, "type": etype})
            seen.add(name)

        return cleaned

    def _clean_relationships(self, relationships: List[Dict]) -> List[Dict]:
        allowed_types = {
            "defines", "has_component", "has_step",
            "part_of", "example_of", "used_in",
            "supports", "objective_of", "cause_of"
        }

        cleaned = []
        seen = set()

        for r in relationships:
            if not isinstance(r, dict):
                continue

            frm = r.get("from", "").strip()
            to = r.get("to", "").strip()
            rtype = r.get("type", "part_of").lower().strip()

            if not frm or not to or frm == to:
                continue

            if rtype not in allowed_types:
                continue

            key = f"{frm}|{rtype}|{to}"
            if key in seen:
                continue

            cleaned.append({"from": frm, "to": to, "type": rtype})
            seen.add(key)

        return cleaned

    def process_text_chunks(self, chunks: List[str], user_id: str) -> Dict[str, int]:
        neo4j_client.create_user_if_not_exists(user_id)

        total_entities = 0
        total_relationships = 0
        processed = 0

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")

            entities, relationships = self.extract_entities_relationships(chunk, user_id)

            if entities or relationships:
                neo4j_client.create_entities(entities, user_id)
                neo4j_client.create_relationships(relationships, user_id)

                total_entities += len(entities)
                total_relationships += len(relationships)
                processed += 1

        return {
            "processed_chunks": processed,
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "success": True
        }

    def extract_from_single_text(self, text: str, user_id: str) -> Dict[str, Any]:
        chunks = semantic_chunk(text)

        if not chunks:
            return {
                "processed_chunks": 0,
                "total_entities": 0,
                "total_relationships": 0,
                "success": False
            }

        return self.process_text_chunks(chunks, user_id)


kg_extractor = KnowledgeGraphExtractor()