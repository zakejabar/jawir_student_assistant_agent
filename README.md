# BinusBrain - Personal Knowledge Graph RAG System

🧠 **A personal knowledge graph system for students to upload documents, build knowledge graphs, and query their materials using AI.**

## ✨ Features

- **📁 File Upload & OCR**: Upload PDF, TXT, or images (screenshots) with automatic text extraction
- **🕸️ Knowledge Graph**: Build personal knowledge graphs from your documents using LLM entity extraction
- **💬 Smart Querying**: Ask questions about your materials with hybrid vector + graph search
- **📊 Interactive Visualization**: Explore your knowledge graph with interactive PyVis visualization
- **🔒 User Isolation**: Each user gets their own private knowledge graph

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Start Neo4j (required for graph database)
neo4j start
# Default credentials: neo4j / neo4j

# Get OpenRouter API key (free tier available)
# Sign up at https://openrouter.ai and get your API key
```

### 2. Setup Environment

```bash
# Clone/download the project
cd binusbrain

# Copy environment template
cp .env.example .env

# Edit .env file with your OpenRouter API key
OPENROUTER_API_KEY=your_api_key_here

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📋 Usage Guide

### Upload Materials
1. Go to "📁 Upload Materials" section
2. Choose PDF, TXT, or image files
3. Click "🚀 Process & Index"
4. Wait for knowledge graph extraction

### Ask Questions
1. Go to "💬 Ask Questions About Your Materials"
2. Type your question about your uploaded documents
3. Get AI-powered answers with context from your materials

### Visualize Knowledge Graph
1. Go to "🕸️ Knowledge Graph Visualization"
2. Click "🎨 Visualize Graph"
3. Explore your interactive knowledge graph

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit (Python web UI)
- **LLM**: OpenRouter (Free Llama models)
- **Graph Database**: Neo4j
- **OCR**: EasyOCR
- **Vector Search**: Sentence Transformers
- **Visualization**: PyVis
- **Agent**: LangGraph (workflow orchestration)

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  LangGraph Agent │────│   Neo4j Graph   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ File Upload +   │    │ LLM Entity/Rel   │    │ User-Specific   │
│ OCR Processing  │    │ Extraction       │    │ Graph Storage   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Text Chunking   │    │ Vector + Graph   │    │ PyVis Graph     │
│ & Preparation   │    │ Hybrid Search    │    │ Visualization   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
binusbrain/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── config/
│   ├── neo4j_config.py   # Neo4j connection config
│   └── llm_config.py     # OpenRouter LLM config
└── src/
    ├── agent.py          # LangGraph workflow agent
    ├── upload_handler.py # File upload + OCR processing
    ├── kg_extractor.py   # LLM entity/relationship extraction
    ├── neo4j_client.py   # Direct Neo4j operations
    ├── query_engine.py   # Hybrid vector + graph search
    └── graph_viz.py      # PyVis knowledge graph visualization
```

## 🎯 Key Features Explained

### 1. Lightweight Knowledge Graph Extraction
Instead of using heavy Microsoft GraphRAG, we use:
- **LLM Entity Extraction**: Extract entities and relationships using OpenRouter Llama
- **Direct Neo4j Storage**: Store directly to Neo4j (no indexing pipeline)
- **User Isolation**: Each user gets separate graph namespace
- **Fast Processing**: 5-30 seconds per document vs. minutes for GraphRAG

### 2. Hybrid Query Engine
- **Vector Similarity**: Find relevant document chunks using embeddings
- **Graph Context**: Get related entities and relationships from knowledge graph
- **LLM Answer Generation**: Combine both contexts for comprehensive answers

### 3. Interactive Knowledge Graph
- **Real-time Visualization**: Interactive network graph using PyVis
- **Node Sizing**: Size based on connection count
- **Color Coding**: Different colors for entity types
- **Graph Statistics**: Nodes, edges, and type breakdowns

## ⚙️ Configuration

### Environment Variables (.env)
```bash
OPENROUTER_API_KEY=your_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j
USER_SESSION_TIMEOUT=3600
MAX_FILE_SIZE_MB=10
```

### Neo4j Setup
1. Download Neo4j Desktop (free)
2. Create new database with default credentials
3. Run: `neo4j start`
4. Access at: `http://localhost:7474`

### OpenRouter Setup
1. Sign up at https://openrouter.ai
2. Add $10 credits (or use free tier)
3. Get API key from "Keys" section
4. We use: `meta-llama/llama-3.1-8b-instruct` (free tier)

## 🔧 Development

### Testing Components
```python
# Test Neo4j connection
from config.neo4j_config import neo4j_config
print(neo4j_config.test_connection())

# Test LLM connection
from config.llm_config import llm_config
success, response = llm_config.test_connection()
print(f"LLM working: {success}")

# Test upload handler
from src.upload_handler import upload_handler
text, type = upload_handler.process_upload(file_data, filename, user_id)
```

### Customization
- **LLM Model**: Change in `config/llm_config.py`
- **Entity Types**: Modify in `src/kg_extractor.py`
- **UI Styling**: Edit CSS in `app.py`
- **Graph Colors**: Update in `src/graph_viz.py`

## 🚨 Troubleshooting

### Common Issues

**Neo4j Connection Failed**
```bash
# Check if Neo4j is running
neo4j status
neo4j start  # Start if not running
```

**OpenRouter API Error**
```bash
# Verify API key
echo $OPENROUTER_API_KEY
# Check OpenRouter dashboard for credits
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Memory Issues with EasyOCR**
- EasyOCR loads large models on first use
- First OCR call may take 30-60 seconds
- Subsequent calls are much faster

## 📊 Performance

- **Upload Processing**: 5-30 seconds per document
- **Query Response**: 2-10 seconds
- **Graph Visualization**: Instant (cached data)
- **Storage**: ~1KB per entity, ~500B per relationship

## 🔒 Security & Privacy

- **User Isolation**: Each user gets separate graph namespace
- **Local Processing**: Most processing happens locally
- **No Data Persistence**: Uploaded files are not stored permanently
- **API Keys**: Stored in environment variables only

## 📈 Future Enhancements

- [ ] User authentication system
- [ ] Collaborative knowledge graphs
- [ ] Advanced graph analytics
- [ ] Export to other formats (GraphML, etc.)
- [ ] Multi-language OCR support
- [ ] Real-time collaboration features

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure Neo4j and OpenRouter are properly configured
4. Check console logs for detailed error messages

---

**Built with ❤️ for students who want to organize and explore their learning materials using AI-powered knowledge graphs.**
