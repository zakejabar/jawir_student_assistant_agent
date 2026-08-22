# StudyMate

Upload study materials, let an LLM build a knowledge graph from them in Neo4j, then ask questions answered from your own documents.

## What problem it solves

Notes, slides, and PDFs pile up as disconnected files, and plain keyword search doesn't show how ideas relate. StudyMate extracts the concepts and relationships out of your materials into a per-user graph, so you can both **ask questions** and **see the connections** between topics. It's a prototype — a single-session Streamlit demo, not a hosted product.

## How it works

The pipeline (real code path, not idealized):

```
Streamlit UI (app.py)
  -> StudyMateAgent facade (src/agent_interface.py)
  -> LangGraph workflow (src/agent_runner.py): route -> {upload+extract | query | visualize}

UPLOAD:  extract text  (PDF via PyMuPDF, PPTX via python-pptx, images via EasyOCR, txt decode)
      -> chunk         (LangChain RecursiveCharacterTextSplitter, 2000 chars / 200 overlap)
      -> extract       (LLM returns JSON entities + relationships, validated against fixed type lists)
      -> store         (Neo4j, isolated per user via a dynamic label `User_<id>`)

QUERY:   LLM names the main concept in the question
      -> look up that concept's 1-hop neighborhood in the graph
      -> if the graph has nothing, fall back to embedding search
         (SentenceTransformers all-MiniLM-L6-v2 + cosine similarity)
      -> LLM writes the answer from that context
```

Retrieval is **graph-first, vector-fallback**. Each user's data is separated by a Neo4j label rather than a property filter.

## Quickstart

**Prerequisites:** Python 3.12, a running Neo4j instance, and an [OpenRouter API key](https://openrouter.ai/keys).

```bash
# 1. Neo4j (example: Docker)
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password neo4j:5

# 2. Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # heavy: pulls in torch via easyocr + sentence-transformers

# 3. Configure
cp .env.example .env              # then edit .env:
#   OPENROUTER_API_KEY=sk-or-...
#   NEO4J_PASSWORD=your_password

# 4. Run
streamlit run app.py              # opens http://localhost:8501
```

## Example (real run)

**Input** — a plain-text lecture note on Integrated Marketing Communications (excerpt):

> The promotion mix is the set of tools a company uses to communicate customer value... The promotion mix has five main components: advertising, sales promotion, personal selling, public relations, and direct marketing.

**After upload+extract** — 17 entities, 18 relationships written to the graph, including:

```
Promotion Mix --has_component--> Advertising
Promotion Mix --has_component--> Sales Promotion
Promotion Mix --has_component--> Personal Selling
Promotion Mix --has_component--> Public Relations
Promotion Mix --has_component--> Direct Marketing
Advertising   --example_of-->    Television Commercials
Integrated Marketing Communications --defines--> Promotion Mix
```

**Question:** *"What are the components of the promotion mix?"*

**Answer (verbatim, trimmed):**

> **Definition:** The promotion mix refers to the set of tools a company uses to communicate customer value and build customer relationships.
> **Components / Tools:** Direct Marketing, Personal Selling, Public Relations, Sales Promotion, Advertising.
> **Integration Levels:** Internal Integration, External Integration, Channel Integration...
> **Example:** A company like Nike uses a well-coordinated promotion mix...

The five components are correct and grounded in the document. Note the "Integration Levels" and "Nike" parts were **not** in the source — see Status.

## Status

Works:
- Text extraction for PDF, PPTX, TXT, and images (OCR).
- LLM entity/relationship extraction into Neo4j with per-user isolation.
- Graph-first + vector-fallback query, answered by the LLM.
- PyVis graph visualization and JSON export.

Known limitations (honest):
- **Answers can hallucinate beyond the source.** The answer template forces six fixed sections (Definition/Objectives/Components/Integration Levels/Benefits/Example), so the model invents content to fill sections the document doesn't cover, despite a "use only the context" instruction. Retrieval is grounded; generation over-reaches.
- **Vector search doesn't scale.** Chunk embeddings are stored in Neo4j but ignored at query time — every query re-embeds all of the user's chunks in memory. Fine for a demo, not for large corpora.
- **Single-session demo.** User identity is an auto-generated timestamp; there's no real auth, and per-user Neo4j *labels* (rather than a property filter) are an unusual choice that won't scale to many users.
- Some orphaned modules remain (`src/agent/intent_classifier.py`, `kg_retriever.py`).

## Tech

Python 3.12 · Streamlit · LangGraph · LangChain · OpenRouter (Llama 3.1 8B) · Neo4j · SentenceTransformers (all-MiniLM-L6-v2) · EasyOCR · PyMuPDF · python-pptx · PyVis · scikit-learn
