# BinusBrain - Complete System Guide

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [File Structure & Relationships](#file-structure--relationships)
3. [Detailed File Explanations](#detailed-file-explanations)
4. [Data Flow & Workflows](#data-flow--workflows)
5. [Configuration Management](#configuration-management)
6. [Integration Patterns](#integration-patterns)
7. [Error Handling & Logging](#error-handling--logging)

---

## 🏗️ System Overview

BinusBrain is a **Personal Knowledge Graph RAG (Retrieval-Augmented Generation) System** that allows Binus students to:
- Upload documents (PDF, TXT, images)
- Automatically extract knowledge using AI
- Build personal knowledge graphs
- Query materials using hybrid RAG
- Visualize relationships interactively

**Tech Stack**: LangGraph + OpenRouter Llama + Neo4j + Streamlit + EasyOCR + PyVis

---

## 📁 File Structure & Relationships

```
📦 BinusBrain System
├── 🎨 app.py                          # MAIN ENTRY POINT - Streamlit Web Interface
│   ├── Imports: src.*, config.*
│   ├── Uses: binus_agent, graph_visualizer
│   └── Calls: All modules through agent
│
├── 📄 requirements.txt                 # Python Dependencies
│   ├── langgraph, langchain           # Workflow & LLM integration
│   ├── neo4j                          # Graph database
│   ├── streamlit                      # Web UI framework
│   ├── easyocr                        # OCR for images
│   ├── pyvis                          # Graph visualization
│   └── sentence-transformers          # Vector embeddings
│
├── 🔧 config/
│   ├── llm_config.py                  # OpenRouter Configuration
│   │   ├── Uses: ChatOpenAI from langchain-openai
│   │   ├── Provides: llm_config.get_llm()
│   │   └── Used by: kg_extractor, query_engine
│   │
│   └── neo4j_config.py                # Neo4j Database Configuration
│       ├── Uses: neo4j Python driver
│       ├── Provides: neo4j_config.get_driver()
│       └── Used by: neo4j_client
│
├── 🧠 src/
│   ├── agent.py                       # LANGGRAPH WORKFLOW ORCHESTRATOR
│   │   ├── Uses: All other src modules
│   │   ├── Provides: binus_agent (global instance)
│   │   ├── Called by: app.py
│   │   └── Manages: StateGraph workflow
│   │
│   ├── upload_handler.py              # FILE PROCESSING & OCR
│   │   ├── Uses: easyocr, PIL, fitz (PyMuPDF)
│   │   ├── Provides: upload_handler (global instance)
│   │   ├── Used by: agent.py
│   │   └── Handles: PDF, TXT, Image extraction
│   │
│   ├── kg_extractor.py                # AI KNOWLEDGE EXTRACTION
│   │   ├── Uses: llm_config, neo4j_client
│   │   ├── Provides: kg_extractor (global instance)
│   │   ├── Used by: agent.py
│   │   └── Handles: Entity/relationship extraction via LLM
│   │
│   ├── query_engine.py                # HYBRID RAG QUERY SYSTEM
│   │   ├── Uses: llm_config, neo4j_client, sentence_transformers
│   │   ├── Provides: query_engine (global instance)
│   │   ├── Used by: agent.py
│   │   └── Handles: Vector search + Graph traversal
│   │
│   ├── graph_viz.py                   # INTERACTIVE GRAPH VISUALIZATION
│   │   ├── Uses: pyvis, neo4j_client
│   │   ├── Provides: graph_visualizer (global instance)
│   │   ├── Used by: agent.py, app.py
│   │   └── Handles: Network graph generation & display
│   │
│   └── neo4j_client.py                # GRAPH DATABASE OPERATIONS
│       ├── Uses: neo4j_config
│       ├── Provides: neo4j_client (global instance)
│       ├── Used by: agent.py, kg_extractor, query_engine, graph_viz
│       └── Handles: All Neo4j CRUD operations
│
├── 📚 Documentation
│   ├── README.md                      # Project overview & setup
│   ├── TODO.md                        # Development roadmap
│   ├── SYSTEM_OVERVIEW.md             # High-level system description
│   └── COMPLETE_SYSTEM_GUIDE.md       # This comprehensive guide
```

---

## 📄 Detailed File Explanations

### 🎨 **app.py** - Main Streamlit Application
**Purpose**: Primary web interface and application entry point

**Key Responsibilities**:
- Renders Streamlit UI with upload, chat, and visualization sections
- Manages user sessions and state
- Handles file uploads and user interactions
- Calls binus_agent for all operations
- Provides system status monitoring

**Dependencies**:
- `streamlit` for web framework
- `src.agent` for workflow execution
- `src.graph_viz` for visualization rendering
- `config.neo4j_config` and `config.llm_config` for system checks

**Key Functions**:
- `initialize_session_state()`: Sets up user session
- `check_dependencies()`: Validates Neo4j and LLM connections
- `render_upload_section()`: File upload UI
- `render_chat_section()`: Query interface
- `render_visualization_section()`: Graph display
- `render_sidebar()`: Controls and status

**Data Flow**: User Input → Streamlit UI → binus_agent.invoke() → Display Results

---

### 🧠 **src/agent.py** - LangGraph Workflow Orchestrator
**Purpose**: Central state machine managing all system workflows

**Key Responsibilities**:
- Implements LangGraph StateGraph with conditional routing
- Orchestrates upload → processing → knowledge extraction workflow
- Manages query → RAG → response workflow
- Handles visualization data retrieval
- Provides error handling and state management

**Dependencies**:
- `langgraph.graph` for workflow orchestration
- `src.upload_handler` for file processing
- `src.kg_extractor` for knowledge extraction
- `src.query_engine` for RAG queries
- `src.graph_viz` for visualization data
- `src.neo4j_client` for database operations

**AgentState Structure**:
```python
{
    "user_id": str,           # User identifier
    "action": str,            # "upload", "query", or "visualize"
    "file_data": bytes,       # Uploaded file content
    "filename": str,          # Original filename
    "extracted_text": str,    # Processed text content
    "processing_result": dict,# Knowledge extraction results
    "question": str,          # User query
    "query_result": dict,     # RAG response
    "graph_data": dict,       # Visualization data
    "messages": list,         # Conversation history
    "error": str,             # Error messages
    "success": bool           # Operation status
}
```

**Workflow Nodes**:
1. `route_action`: Routes to appropriate handler based on action type
2. `process_upload`: Handles file processing and text extraction
3. `extract_knowledge`: Runs AI knowledge extraction
4. `query_materials`: Executes hybrid RAG queries
5. `get_graph_data`: Retrieves visualization data
6. `handle_error`: Graceful error handling

**Key Methods**:
- `upload_file()`: Convenience method for file uploads
- `query_materials()`: Convenience method for queries
- `get_graph_data()`: Convenience method for visualization

---

### 📄 **src/upload_handler.py** - File Processing & OCR
**Purpose**: Extract text from various file formats including OCR for images

**Key Responsibilities**:
- Process PDF files using PyMuPDF
- Handle text file reading with encoding support
- Perform OCR on images using EasyOCR
- Clean and normalize extracted text
- Chunk text for optimal processing

**Dependencies**:
- `easyocr` for OCR functionality
- `PIL (Pillow)` for image handling
- `fitz (PyMuPDF)` for PDF processing
- `io` for byte stream handling

**Supported Formats**:
- **PDF**: Text extraction using PyMuPDF (better than PyPDF2)
- **TXT/MD**: Direct text reading with UTF-8 handling
- **Images**: OCR extraction from PNG, JPG, JPEG, BMP, TIFF

**Key Methods**:
- `extract_text_from_pdf()`: PDF text extraction
- `extract_text_from_txt()`: Plain text file handling
- `extract_text_from_image()`: OCR processing
- `process_upload()`: Main entry point for file processing
- `clean_text()`: Text normalization and noise removal
- `chunk_text()`: Split text for optimal knowledge extraction

**Text Processing Pipeline**:
1. File type detection by extension
2. Format-specific extraction
3. Text cleaning and normalization
4. Optional chunking for large texts
5. Return (extracted_text, file_type)

---

### 🔍 **src/kg_extractor.py** - AI Knowledge Extraction
**Purpose**: Extract entities and relationships from text using LLM

**Key Responsibilities**:
- Use LLM to identify entities (concepts, people, terms)
- Extract relationships between entities
- Clean and validate extracted data
- Store results in Neo4j with user isolation
- Handle text chunking for large documents

**Dependencies**:
- `config.llm_config` for LLM access
- `src.neo4j_client` for data storage
- `json` for response parsing
- `re` for text cleaning

**LLM Extraction Prompt**:
```python
extraction_prompt = f"""
Extract entities and relationships from text focusing on:
- Key concepts, terms, definitions
- Important people, places, organizations  
- Cause-effect relationships
- Part-whole relationships
- Related concepts

Return JSON: {{"entities": [...], "relationships": [...]}}
"""
```

**Entity Types Supported**:
- `concept`: Abstract ideas, theories
- `person`: Individual names
- `place`: Locations, addresses
- `organization`: Institutions, companies
- `term`: Technical terminology
- `definition`: Explanatory content

**Relationship Types Supported**:
- `relates_to`: General connection
- `part_of`: Component relationship
- `cause_of`: Causal connection
- `example_of`: Instance relationship
- `defines`: Definitional relationship
- `contains`: Container relationship

**Key Methods**:
- `extract_entities_relationships()`: Core LLM extraction
- `process_text_chunks()`: Batch processing for large texts
- `extract_from_single_text()`: Single document processing
- `_clean_entities()`: Entity validation and deduplication
- `_clean_relationships()`: Relationship validation
- `_clean_json_response()`: LLM response parsing

---

### 🤖 **src/query_engine.py** - Hybrid RAG Query System
**Purpose**: Combine vector similarity and graph traversal for comprehensive answers

**Key Responsibilities**:
- Perform vector similarity search on document chunks
- Extract entities from user queries
- Find related concepts in knowledge graph
- Generate answers using LLM with combined context
- Provide query statistics and debugging info

**Dependencies**:
- `config.llm_config` for LLM access
- `src.neo4j_client` for graph data access
- `sentence_transformers` for embeddings
- `sklearn.metrics.pairwise` for similarity calculation
- `numpy` for vector operations

**Hybrid RAG Architecture**:
```
1. Vector Search Layer:
   - Convert query to embeddings using SentenceTransformer
   - Compare against stored document chunk embeddings
   - Return top-k most similar chunks

2. Graph Search Layer:
   - Extract entities from query
   - Find related entities in user's knowledge graph
   - Retrieve relationships between concepts

3. LLM Synthesis Layer:
   - Combine vector results + graph context
   - Generate comprehensive answer
   - Provide source attribution
```

**Key Methods**:
- `vector_search()`: Semantic similarity search
- `get_graph_context()`: Graph-based entity/relationship lookup
- `generate_answer()`: Main RAG query handler
- `_extract_query_entities()`: Simple entity extraction from queries
- `encode_texts()`: Text embedding generation

**Query Processing Pipeline**:
1. Vector similarity search (semantic matching)
2. Graph traversal (related concepts)
3. Context combination (documents + graph)
4. LLM answer generation
5. Return with statistics

---

### 🕸️ **src/graph_viz.py** - Interactive Graph Visualization
**Purpose**: Create interactive network visualizations of knowledge graphs

**Key Responsibilities**:
- Convert Neo4j graph data to interactive network format
- Apply color coding by entity type
- Calculate node sizes based on connectivity
- Generate physics-based layout
- Render in Streamlit with custom styling
- Provide graph statistics and export capabilities

**Dependencies**:
- `pyvis.network` for interactive graphs
- `src.neo4j_client` for graph data retrieval
- `streamlit` for web rendering
- `json` for data serialization

**Visualization Features**:
- **Color Coding**: Different colors for entity types
- **Node Sizing**: Based on number of connections
- **Physics Simulation**: Barnes-Hut layout algorithm
- **Interactive Controls**: Zoom, drag, hover details
- **Custom Styling**: Dark theme with proper contrast

**Node Color Scheme**:
```python
colors = {
    'concept': '#FF6B6B',      # Red
    'person': '#4ECDC4',       # Teal
    'place': '#45B7D1',        # Blue
    'organization': '#96CEB4', # Green
    'term': '#FFEAA7',         # Yellow
    'definition': '#DDA0DD'    # Purple
}
```

**Key Methods**:
- `create_network_graph()`: Generate PyVis network
- `render_graph_in_streamlit()`: Display in web interface
- `_calculate_node_size()`: Size based on connectivity
- `_render_legend()`: Show entity type legend
- `_render_graph_stats()`: Display graph statistics
- `export_graph_data()`: Export for external use

**Network Configuration**:
- Physics: Barnes-Hut gravity simulation
- Node borders: 2px width, white text
- Edge styling: Smooth curves, hover highlighting
- Layout: Force-directed with stabilization

---

### 🗄️ **src/neo4j_client.py** - Graph Database Operations
**Purpose**: Handle all Neo4j database operations with user data isolation

**Key Responsibilities**:
- Manage Neo4j driver connection
- Create user nodes and ensure data isolation
- Store entities with type classification
- Create relationships between entities
- Query graph data for visualization
- Provide CRUD operations for all graph data

**Dependencies**:
- `config.neo4j_config` for database connection
- `json` for data serialization
- `typing` for type hints

**Database Schema**:
```cypher
// User nodes
(u:User {id: "student_20241215_143022"})

// Entity nodes with user isolation
(e:Entity:User_student_20241215_143022 {
    name: "Algorithm",
    type: "concept",
    user_id: "student_20241215_143022",
    created_at: datetime()
})

// Relationships with user isolation
(a:Entity:User_student_20241215_143022)-[r:RELATES {
    type: "relates_to",
    user_id: "student_20241215_143022", 
    created_at: datetime()
}]->(b:Entity:User_student_20241215_143022)
```

**User Data Isolation**:
- All entity nodes labeled with `User_{user_id}`
- All relationships scoped to specific user
- User ID stored as property for additional filtering
- Clean separation prevents data leakage

**Key Methods**:
- `create_user_if_not_exists()`: Initialize user in database
- `create_entities()`: Bulk entity creation with type setting
- `create_relationships()`: Bulk relationship creation
- `get_user_entities()`: Retrieve user's entities with limit
- `get_user_relationships()`: Retrieve user's relationships
- `get_user_graph_data()`: Complete graph for visualization
- `delete_user_data()`: Clean user data (testing/reset)

**Connection Management**:
- Uses Neo4j driver with connection pooling
- Session-based transactions for data consistency
- Automatic driver closing on cleanup

---

### ⚙️ **config/llm_config.py** - OpenRouter LLM Configuration
**Purpose**: Configure and manage OpenRouter LLM access for AI operations

**Key Responsibilities**:
- Load OpenRouter API credentials from environment
- Configure ChatOpenAI client for OpenRouter
- Provide consistent LLM access across modules
- Handle connection testing and error management

**Dependencies**:
- `langchain_openai.ChatOpenAI` for LLM client
- `python-dotenv` for environment variable loading
- `os` for environment variable access

**Configuration Details**:
- **Model**: `meta-llama/llama-3.1-8b-instruct` (FREE tier)
- **API Base**: `https://openrouter.ai/api/v1`
- **Temperature**: `0.1` (consistent for extraction tasks)
- **Max Tokens**: `2000` (sufficient for most responses)

**Key Methods**:
- `get_llm()`: Returns configured ChatOpenAI instance
- `test_connection()`: Validates API connectivity

**Environment Variables**:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

---

### 🗄️ **config/neo4j_config.py** - Neo4j Database Configuration
**Purpose**: Configure and manage Neo4j database connections

**Key Responsibilities**:
- Load Neo4j connection parameters
- Create and manage database driver
- Handle connection testing and error management
- Provide consistent database access

**Dependencies**:
- `neo4j` Python driver
- `python-dotenv` for environment variables
- `os` for environment variable access

**Configuration Details**:
- **URI**: `bolt://localhost:7687` (default Neo4j)
- **Authentication**: neo4j/neo4j (default credentials)
- **Connection Pooling**: Configured for optimal performance

**Key Methods**:
- `get_driver()`: Returns configured Neo4j driver
- `test_connection()`: Validates database connectivity

**Environment Variables**:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

---

## 🔄 Data Flow & Workflows

### 📤 **Upload Workflow**
```mermaid
graph TD
    A[User uploads file] --> B[app.py receives upload]
    B --> C[binus_agent.upload_file()]
    C --> D[agent routes to process_upload]
    D --> E[upload_handler.process_upload()]
    E --> F[Extract text (PDF/TXT/OCR)]
    F --> G[agent routes to extract_knowledge]
    G --> H[kg_extractor.extract_from_single_text()]
    H --> I[LLM extracts entities/relationships]
    I --> J[neo4j_client.create_entities/relationships()]
    J --> K[Return success with statistics]
    K --> L[Display in Streamlit UI]
```

### ❓ **Query Workflow**
```mermaid
graph TD
    A[User asks question] --> B[app.py receives query]
    B --> C[binus_agent.query_materials()]
    C --> D[agent routes to query_materials]
    D --> E[query_engine.generate_answer()]
    E --> F[Vector similarity search]
    F --> G[Graph context retrieval]
    G --> H[LLM generates answer]
    H --> I[Return answer + context]
    I --> J[Display in Streamlit UI]
```

### 🕸️ **Visualization Workflow**
```mermaid
graph TD
    A[User clicks visualize] --> B[app.py calls graph_viz]
    B --> C[binus_agent.get_graph_data()]
    C --> D[agent routes to get_graph_data]
    D --> E[neo4j_client.get_user_graph_data()]
    E --> F[graph_viz.create_network_graph()]
    F --> G[PyVis generates interactive graph]
    G --> H[Display in Streamlit with styling]
```

---

## ⚙️ Configuration Management

### 🔐 **Environment Variables**
```bash
# Required for LLM operations
OPENROUTER_API_KEY=your_openrouter_api_key

# Neo4j database configuration  
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 📦 **Dependencies by Module**
```python
# app.py
streamlit, src.agent, src.graph_viz, config.*

# agent.py
langgraph, langchain-core, src.*

# upload_handler.py
easyocr, PIL, fitz, io

# kg_extractor.py
config.llm_config, src.neo4j_client, json, re

# query_engine.py
config.llm_config, src.neo4j_client, sentence-transformers, sklearn, numpy

# graph_viz.py
pyvis, src.neo4j_client, streamlit, json

# neo4j_client.py
config.neo4j_config, json, typing

# llm_config.py
langchain-openai, python-dotenv, os

# neo4j_config.py
neo4j, python-dotenv, os
```

---

## 🔗 Integration Patterns

### 📡 **Module Communication**
- **Global Instances**: Each module exports a global instance (e.g., `binus_agent`, `kg_extractor`)
- **Dependency Injection**: Modules receive dependencies through constructor parameters
- **Interface Consistency**: All modules follow similar method signatures and return patterns

### 🔄 **Error Handling Strategy**
- **Try-Catch Blocks**: All external API calls wrapped in exception handling
- **Graceful Degradation**: System continues operating with partial functionality
- **User Feedback**: Errors displayed in Streamlit UI with helpful messages
- **Logging**: Detailed error information for debugging

### 📊 **State Management**
- **Session State**: Streamlit manages user session data
- **Agent State**: LangGraph manages workflow state
- **Database State**: Neo4j maintains persistent graph data
- **Cache State**: Streamlit caches expensive operations (OCR, embeddings)

---

## 🎯 **System Benefits**

### 🎓 **For Students**
- **Intelligent Document Processing**: OCR for screenshots, automatic text extraction
- **Personal Knowledge Graphs**: Visual representation of concept relationships  
- **Hybrid Querying**: Combines semantic search with graph traversal
- **Interactive Visualization**: Explore knowledge networks visually
- **FREE to Use**: OpenRouter free tier + local processing

### 🔧 **For Developers**
- **Modular Architecture**: Easy to extend and modify
- **LangGraph Workflows**: Clear state management and routing
- **Production Ready**: Error handling, logging, testing support
- **Scalable Design**: Can handle multiple users with proper deployment
- **Open Source**: Complete code available for customization

### 📈 **Performance Characteristics**
- **Upload Processing**: 5-30 seconds (depends on file size)
- **Query Response**: 2-10 seconds (LLM + retrieval)
- **Visualization**: Instant (cached Neo4j data)
- **Memory Usage**: Efficient with connection pooling
- **Storage**: Neo4j handles graph data efficiently

This comprehensive guide covers every aspect of the BinusBrain system, from individual file responsibilities to complete system integration and data flows. The modular architecture makes it easy to understand, extend, and deploy for educational use cases.
