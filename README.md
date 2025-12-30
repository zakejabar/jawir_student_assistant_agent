# StudyMate - Personal Knowledge Graph RAG System

🧠 **Upload your study materials, let AI build a knowledge graph, then ask questions about everything you've learned.**

## What does this do?

- **Upload anything**: PDFs, text files, even screenshots - we'll extract the text automatically
- **Builds a knowledge graph**: The AI finds entities and relationships in your documents and connects them
- **Smart search**: Ask questions and get answers from across all your materials
- **See the connections**: Visualize how everything in your notes relates to each other
- **Your stuff stays yours**: Each user has their own private graph

## Getting Started

### What you need first

```bash
# Start Neo4j (this is your graph database)
neo4j start
# Username and password are both "neo4j" by default

# Get an OpenRouter API key (they have a free tier)
# Go to https://openrouter.ai and sign up
```

### Setting things up

```bash
# Go to your project folder
cd student-rag

# Copy the example environment file
cp .env.example .env

# Open .env and add your keys:
OPENROUTER_API_KEY=your_api_key_here
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Install everything
pip install -r requirements.txt
```

### Run it

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` and you're good to go.

## How to use it

### Adding your materials
1. Click on "📁 Upload Materials"
2. Pick your PDFs, text files, or screenshots
3. Hit "Process & Index"
4. Wait a bit while it builds the knowledge graph

### Asking questions
1. Go to "💬 Ask Questions About Your Materials"
2. Type whatever you want to know
3. Get answers pulled from everything you've uploaded

### Checking out the graph
1. Head to "🕸️ Knowledge Graph Visualization"
2. Click "🎨 Visualize Graph"
3. Play around with the interactive graph - you can see how everything connects

## How it works

### What we're using
- **Frontend**: Streamlit (simple Python web UI)
- **LLM**: OpenRouter (free Llama models)
- **Graph Database**: Neo4j
- **OCR**: EasyOCR (for reading screenshots)
- **Vector Search**: Sentence Transformers
- **Visualization**: PyVis
- **Agent**: LangGraph (handles the workflow)

### The basic flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  LangGraph Agent │────│   Neo4j Graph   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Upload files +  │    │ AI extracts      │    │ Stores in your  │
│ OCR if needed   │    │ entities & links │    │ personal graph  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Breaks text     │    │ Searches both    │    │ Shows you the   │
│ into chunks     │    │ vectors & graph  │    │ visual network  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Folder structure

```
binusbrain/
├── app.py                 # Main app file
├── requirements.txt       # Python packages
├── .env.example          # Template for your settings
├── config/
│   ├── neo4j_config.py   # Neo4j setup
│   └── llm_config.py     # OpenRouter setup
└── src/
    ├── agent.py          # LangGraph workflow
    ├── upload_handler.py # Handles file uploads and OCR
    ├── kg_extractor.py   # Extracts entities and relationships
    ├── neo4j_client.py   # Talks to Neo4j
    ├── query_engine.py   # Searches and answers questions
    └── graph_viz.py      # Makes the visualization
```

## Cool things about this

### Lightweight knowledge graph
We're not using those huge Microsoft GraphRAG pipelines. Instead:
- **Simple LLM extraction**: LLM pulls out entities and relationships
- **Straight to Neo4j**: No complicated indexing pipelines
- **Separate graphs per user**: Your stuff doesn't mix with anyone else's
- **Actually fast**: Takes 5-30 seconds per document instead of several minutes

### Hybrid search
- **Vector similarity**: Finds relevant chunks using embeddings
- **Graph context**: Grabs related entities and their connections
- **AI answers**: Combines everything to give you complete answers

### Interactive visualization
- **Live network graph**: Click and drag nodes around
- **Smart sizing**: Bigger nodes = more connections
- **Color coded**: Different colors for different entity types
- **Stats**: See how many nodes, edges, and entity types you have

## Settings

### Your .env file should look like:
```bash
OPENROUTER_API_KEY=your_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### Setting up Neo4j
1. Download Neo4j Desktop (it's free)
2. Create a new database - it'll give you default credentials
3. Run `neo4j start`
4. You can check it at `http://localhost:7474`

### Getting OpenRouter working
1. Go to https://openrouter.ai and make an account
2. Add $10 in credits (or stick with free tier)
3. Grab your API key from the "Keys" section
4. We're using `meta-llama/llama-3.1-8b-instruct` which is free

## Testing stuff

### Make sure everything's connected
```python
# Test Neo4j
from config.neo4j_config import neo4j_config
print(neo4j_config.test_connection())

# Test LLM
from config.llm_config import llm_config
success, response = llm_config.test_connection()
print(f"LLM working: {success}")

# Test uploads
from src.upload_handler import upload_handler
text, type = upload_handler.process_upload(file_data, filename, user_id)
```

### Want to customize?
- **Different LLM**: Edit `config/llm_config.py`
- **Entity types**: Change in `src/kg_extractor.py`
- **UI look**: Mess with the CSS in `app.py`
- **Graph colors**: Update `src/graph_viz.py`

## When things break

### Neo4j won't connect
```bash
# Check if it's running
neo4j status
neo4j start  # Start it up
```

### OpenRouter errors
```bash
# Make sure your key is set
echo $OPENROUTER_API_KEY
# Check your credits on the OpenRouter dashboard
```

### Python import errors
```bash
# Reinstall everything
pip install -r requirements.txt --force-reinstall
```

### OCR taking forever
- EasyOCR downloads big models the first time you use it
- First OCR might take 30-60 seconds
- After that it's much faster

## Performance

- **Processing uploads**: 5-30 seconds per document
- **Answering questions**: 2-10 seconds
- **Loading visualization**: Pretty much instant
- **Storage**: About 1KB per entity, 500 bytes per relationship

## Privacy stuff

- **Isolated users**: Everyone gets their own graph namespace
- **Local processing**: Most of the work happens on your machine
- **No permanent storage**: We don't save your uploaded files
- **Secure keys**: API keys stay in your environment variables

## What's next

Some ideas for later:
- [ ] Proper user login system
- [ ] Share graphs with classmates
- [ ] Proper Knowledge graph accuracy
- [ ] Better graph analytics
- [ ] Support more languages for OCR
- [ ] Real-time collaborative editing

## Need help?

If something's not working:
1. Check the troubleshooting section above
2. Make sure you installed everything
3. Verify Neo4j and OpenRouter are configured right
4. Look at the console logs - they usually tell you what's wrong

---

**Made for students who want to actually understand and connect their study materials instead of just having a pile of PDFs they never look at again.**
