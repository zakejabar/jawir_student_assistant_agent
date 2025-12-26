# BinusBrain - Personal Knowledge Graph RAG System
## Technical Specification

### 1. System Overview

BinusBrain is a personal knowledge graph RAG (Retrieval-Augmented Generation) system that allows users to upload documents, automatically extract knowledge entities and relationships, and query their personal knowledge base through natural language questions. The system features an interactive knowledge graph visualization and supports multiple document formats.

**Core Technologies:**
- **Frontend:** Streamlit web application
- **Backend:** Python with LangGraph workflow orchestration
- **Database:** Neo4j graph database for knowledge storage
- **LLM:** OpenRouter API (Meta Llama 3.1 8B Instruct)
- **Vector Search:** Sentence Transformers (all-MiniLM-L6-v2)
- **Visualization:** PyVis interactive network graphs
- **Document Processing:** Multi-format text extraction (PDF, PPTX, images, text)

### 2. Architecture

#### 2.1 High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│   Agent Layer   │────│  LangGraph      │
│                 │    │                 │    │  Workflows      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Document Upload │────│ Knowledge Graph │────│   Neo4j Graph   │
│   Processing    │    │   Extraction    │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Query Engine  │────│   Vector Search │────│   LLM Response  │
│  (Hybrid RAG)   │    │                 │    │   Generation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### 2.2 Component Architecture

**Agent Layer (`src/agent/`):**
- `BinusBrainAgent`: Main agent interface with upload/ask/visualize methods
- `agent_runner.py`: LangGraph workflow orchestration
- `intent_classifier.py`: Question intent classification
- `kg_retriever.py`: Knowledge graph retrieval logic
- `agent_structurer.py`: Context structuring for responses
- `answer_generator.py`: LLM prompt generation

**Core Services:**
- `upload_handler.py`: Multi-format document processing
- `kg_extractor.py`: Knowledge graph extraction from text
- `query_engine.py`: Hybrid vector + graph query processing
- `neo4j_client.py`: Graph database operations
- `graph_viz.py`: Interactive visualization generation

**Configuration:**
- `config/llm_config.py`: OpenRouter LLM configuration
- `config/neo4j_config.py`: Neo4j database configuration

**Utilities:**
- `src/chunking/semantic_chunker.py`: Intelligent text chunking

### 3. Data Flow

#### 3.1 Document Upload Flow

```
User Upload → Text Extraction → Semantic Chunking → Entity/Relationship Extraction → Neo4j Storage
```

1. **Text Extraction**: Multi-format processing
   - PDF: PyMuPDF (fitz)
   - PowerPoint: python-pptx
   - Images: EasyOCR
   - Text: Direct UTF-8 decoding

2. **Semantic Chunking**: Intelligent text segmentation
   - Heading detection (ALL CAPS, numbered, title case)
   - Sentence boundary preservation
   - Maximum chunk size: 6000 characters

3. **Knowledge Extraction**: LLM-powered entity/relationship extraction
   - Entity Types: concept, framework, definition, learning_objective, organization, example, process, step
   - Relationship Types: defines, has_component, has_step, part_of, example_of, used_in, supports, objective_of, cause_of

4. **Graph Storage**: User-isolated Neo4j storage
   - Nodes: `Entity:User_{user_id}`
   - Relationships: `RELATES` with user_id property

#### 3.2 Query Processing Flow

```
User Question → Intent Classification → Concept Extraction → Graph Context + Vector Search → Answer Generation
```

1. **Intent Classification**: Determine query type
   - framework_overview, concept_explanation, comparison, step_by_step, example_case, ethical_reasoning

2. **Concept Extraction**: Identify main academic concept from question

3. **Hybrid Retrieval**:
   - **Graph Context**: Retrieve related entities and relationships from Neo4j
   - **Vector Search**: Semantic similarity search on document chunks
   - **Similarity Threshold**: 0.1 minimum relevance score

4. **Answer Generation**: LLM synthesis with structured context

#### 3.3 Visualization Flow

```
User Request → Neo4j Query → Graph Data → PyVis Network → HTML Rendering
```

### 4. Database Schema

#### 4.1 Neo4j Node Types

**User Node:**
```
(u:User {id: "student_20241213_143022"})
```

**Entity Node:**
```
(e:Entity:User_student_20241213_143022 {
  name: "Integrated Marketing Communications",
  type: "concept",
  user_id: "student_20241213_143022",
  created_at: datetime()
})
```

**Chunk Node (for vector search):**
```
(c:Chunk:User_student_20241213_143022 {
  id: "chunk_001",
  text: "Document text content...",
  embedding: "[0.1, 0.2, ...]",
  user_id: "student_20241213_143022"
})
```

#### 4.2 Neo4j Relationship Types

**Entity Relationships:**
```
(a:Entity)-[r:RELATES {
  type: "has_component",
  user_id: "student_20241213_143022",
  created_at: datetime()
}]->(b:Entity)
```

### 5. API Interfaces

#### 5.1 Agent Interface

```python
class BinusBrainAgent:
    def upload(self, user_id: str, file_data: bytes, filename: str) -> dict:
        # Process and index document

    def ask(self, user_id: str, question: str) -> dict:
        # Generate answer from knowledge base

    def visualize(self, user_id: str) -> dict:
        # Return graph data for visualization
```

#### 5.2 LangGraph Workflow States

```python
class AgentState(TypedDict):
    user_id: str
    action: str  # "upload", "query", "visualize"

    # Upload state
    file_data: Optional[bytes]
    filename: Optional[str]
    extracted_text: Optional[str]
    file_type: Optional[str]
    processing_result: Optional[dict]

    # Query state
    question: Optional[str]
    query_result: Optional[dict]

    # Visualization state
    graph_data: Optional[dict]

    # Control state
    messages: Annotated[list, "conversation messages"]
    error: Optional[str]
    success: bool
```

### 6. Key Algorithms

#### 6.1 Semantic Chunking Algorithm

- **Heading Detection**: Regex patterns for academic document structure
- **Boundary Preservation**: Sentence-ending priority (. ! ?)
- **Overlap Strategy**: 50-character overlap between chunks
- **Size Limits**: Maximum 6000 characters per chunk

#### 6.2 Entity Extraction Prompt

```python
extraction_prompt = f"""
Extract ONLY study-relevant knowledge from academic materials.
Focus on: core concepts, frameworks, definitions, learning objectives, examples.

Return JSON: {{"entities": [...], "relationships": [...]}}
"""
```

#### 6.3 Hybrid Query Algorithm

1. Extract main concept from question
2. Retrieve graph neighborhood (depth=2)
3. Perform vector similarity search (top-k=5)
4. Combine graph context + vector results
5. Generate structured prompt for LLM

#### 6.4 Graph Visualization Algorithm

- **Node Sizing**: Based on connection count (15 + connections × 3)
- **Color Coding**: Entity type-based coloring
- **Layout**: Physics-based network layout
- **Interactivity**: PyVis HTML generation

### 7. Configuration

#### 7.1 Environment Variables

```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=neo4j

# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
```

#### 7.2 Model Configuration

```python
# LLM Settings
model = "meta-llama/llama-3.1-8b-instruct"
temperature = 0.1
max_tokens = 2000

# Vector Search
embedding_model = "all-MiniLM-L6-v2"
similarity_threshold = 0.1
top_k_results = 5
```

### 8. Performance Characteristics

#### 8.1 Processing Limits

- **Document Size**: Limited by memory (no explicit size limits)
- **Chunk Size**: 6000 characters maximum
- **Entity Extraction**: Batch processing with progress tracking
- **Query Response**: ~5-10 seconds typical

#### 8.2 Scalability Considerations

- **User Isolation**: Neo4j labels for multi-tenancy
- **Vector Search**: In-memory embeddings (production: use Pinecone/Weaviate)
- **Concurrent Users**: Limited by Neo4j connection pool
- **Storage**: Neo4j native graph storage

### 9. Error Handling

#### 9.1 Document Processing Errors

- **OCR Failures**: Graceful fallback with error logging
- **Unsupported Formats**: Clear error messages
- **Text Extraction Issues**: Partial processing continuation

#### 9.2 Query Processing Errors

- **No Context Found**: Informative "topic not found" responses
- **LLM API Errors**: Retry logic with exponential backoff
- **Graph Query Failures**: Fallback to vector-only search

#### 9.3 System Health Checks

- **Neo4j Connectivity**: Connection verification on startup
- **LLM API Access**: Test queries during initialization
- **Dependency Validation**: Comprehensive system status reporting

### 10. Security Considerations

#### 10.1 Data Isolation

- **User Scoping**: All data tagged with user_id
- **Neo4j Labels**: User-specific node labels (`User_{user_id}`)
- **Session Management**: Streamlit session state for user tracking

#### 10.2 API Security

- **Environment Variables**: Sensitive credentials in .env files
- **OpenRouter API**: Secure key management
- **No Authentication**: Current implementation (demo purposes)

### 11. Deployment Requirements

#### 11.1 System Requirements

- **Python**: 3.8+
- **Memory**: 4GB+ RAM recommended
- **Storage**: SSD storage for Neo4j
- **Network**: Internet access for OpenRouter API

#### 11.2 External Dependencies

- **Neo4j Database**: Version 5.x+
- **OpenRouter API**: Valid API key with credits
- **Streamlit Sharing**: For cloud deployment (optional)

#### 11.3 Installation Steps

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Start Neo4j
# (Installation instructions in SETUP_GUIDE.md)

# Run application
streamlit run app.py
```

### 12. Future Enhancements

#### 12.1 Planned Features

- **Authentication System**: User management and login
- **Advanced Chunking**: Recursive text splitting algorithms
- **Production Vector DB**: Pinecone/Weaviate integration
- **Multi-modal Processing**: Enhanced image/document understanding
- **Collaborative Features**: Shared knowledge graphs
- **Analytics Dashboard**: Usage statistics and insights

#### 12.2 Performance Optimizations

- **Caching Layer**: Redis for frequent queries
- **Batch Processing**: Parallel entity extraction
- **Index Optimization**: Neo4j schema optimization
- **CDN Integration**: Static asset delivery

#### 12.3 Monitoring & Observability

- **Logging**: Structured logging with log levels
- **Metrics**: Performance monitoring and alerting
- **Health Checks**: Comprehensive system monitoring
- **Error Tracking**: Exception reporting and analysis

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Based on Code Analysis:** All specifications derived from actual implementation in the codebase
