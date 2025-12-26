# BinusBrain System Overview

## 🎯 What This System Does

BinusBrain is a **Personal Knowledge Graph RAG (Retrieval-Augmented Generation) System** that helps Binus students:

1. **Upload Documents** (PDFs, TXT files, images) 
2. **Extract Knowledge** automatically using AI
3. **Build Personal Knowledge Graphs** from their materials
4. **Ask Questions** about their documents
5. **Visualize Relationships** between concepts

## 🏗️ System Architecture

### Core Components:

```
📁 BinusBrain System
├── 🎨 app.py                     # Main Streamlit Web Interface
├── 🧠 src/agent.py               # LangGraph Workflow Orchestrator
├── 📁 config/                    # Configuration Files
│   ├── llm_config.py            # OpenRouter LLM Setup
│   └── neo4j_config.py          # Neo4j Database Config
├── 🔧 Core Modules:
│   ├── upload_handler.py        # File Processing + OCR
│   ├── kg_extractor.py          # AI Knowledge Extraction
│   ├── query_engine.py          # RAG Query System
│   ├── graph_viz.py             # Knowledge Graph Visualization
│   └── neo4j_client.py          # Database Operations
└── 📦 requirements.txt          # Python Dependencies
```

## 🔄 How It Works (Step by Step)

### 1. **Upload Workflow**
```
Student uploads PDF/Image
        ↓
upload_handler.py processes file
        ↓
- If image → EasyOCR extracts text
- If PDF → Text extraction
- If TXT → Direct reading
        ↓
Text goes to Knowledge Graph Extractor
        ↓
kg_extractor.py uses LLM to find:
- Entities (concepts, people, terms)
- Relationships (how things connect)
        ↓
Data stored in Neo4j Graph Database
```

### 2. **Query Workflow**
```
Student asks question
        ↓
query_engine.py searches:
- Vector similarity (find relevant text chunks)
- Graph traversal (find related concepts)
        ↓
Combines both sources as context
        ↓
LLM generates answer using the context
        ↓
Answer returned to student
```

### 3. **Visualization Workflow**
```
Student clicks "Visualize Graph"
        ↓
neo4j_client.py retrieves user's graph data
        ↓
graph_viz.py creates interactive network visualization
        ↓
Shows nodes (entities) and edges (relationships)
```

## 🛠️ Technical Details

### **LangGraph Agent Workflow**
The `src/agent.py` creates a state machine with these nodes:
- `route_action` → Decides what to do (upload/query/visualize)
- `process_upload` → Handles file processing
- `extract_knowledge` → Creates knowledge graph
- `query_materials` → Answers questions
- `get_graph_data` → Prepares visualization data

### **Knowledge Graph Extraction**
- Uses **OpenRouter's Llama model** (FREE tier)
- Processes text in chunks
- Extracts entities like: "Algorithms", "CS101", "Professor Smith"
- Finds relationships like: "CS101 → teaches → Algorithms"
- Stores everything in Neo4j with user isolation

### **Hybrid RAG System**
- **Vector Search**: Finds relevant text passages
- **Graph Search**: Finds related concepts
- **LLM Reasoning**: Combines both for comprehensive answers

### **User-Specific Data**
- Each user gets isolated data in Neo4j
- User ID prefixes all nodes/relationships
- Session-based user management

## 🎨 Web Interface Features

### **Upload Section**
- Drag & drop file upload
- Support for PDF, TXT, PNG, JPG
- Real-time processing status
- Success/error feedback

### **Chat Section**
- Question answering interface
- Chat history display
- Context statistics (documents found, entities used)
- Clear chat option

### **Visualization Section**
- Interactive knowledge graph
- Node clustering by type
- Relationship mapping
- Export functionality

### **Sidebar Controls**
- System status monitoring
- User session management
- Quick statistics
- Help documentation

## 💾 Database Schema (Neo4j)

### Node Types:
```
(User) → User nodes (student_20241215_143022)
(Entity) → Concept/term nodes (Algorithm, CS101)
```

### Relationship Types:
```
(Entity)-[:RELATES_TO]->(Entity)
(Entity)-[:PART_OF]->(Entity) 
(Entity)-[:CAUSE_OF]->(Entity)
(Entity)-[:EXAMPLE_OF]->(Entity)
```

### User Isolation:
- All nodes labeled with User_{user_id}
- All relationships have user_id property

## 🔧 Key Technologies Used

### **Backend**
- **LangGraph**: Workflow orchestration
- **LangChain**: LLM integration
- **Neo4j**: Graph database
- **EasyOCR**: Image text extraction
- **OpenRouter**: FREE LLM API (Llama model)

### **Frontend**
- **Streamlit**: Web UI framework
- **PyVis**: Interactive graph visualization
- **Custom CSS**: Enhanced styling

### **AI/ML**
- **OpenRouter Llama 3.1-8B**: FREE language model
- **Sentence Transformers**: For vector embeddings
- **Custom Prompting**: For entity/relationship extraction

## 💰 Cost Structure (100% FREE)

- **OpenRouter**: FREE tier ($0.50-1.00 for development)
- **Neo4j Community**: FREE (local installation)
- **All processing**: Local except LLM calls
- **Total cost**: Pennies for development

## 🎯 Use Cases

### **For Students:**
1. Upload lecture notes → Ask "What are the key concepts?"
2. Upload textbook chapters → Ask "How do algorithms work?"
3. Upload past papers → Ask "What topics appear frequently?"
4. Visualize relationships → See how concepts connect

### **For Research:**
1. Build knowledge graphs from academic papers
2. Find hidden connections between topics
3. Track concept evolution over time
4. Collaborative knowledge building

## 🚀 Getting Started

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Setup Neo4j**: Install and start Neo4j Desktop
3. **Get OpenRouter Key**: Sign up at openrouter.ai (FREE $10 credits)
4. **Set Environment**: Add OPENROUTER_API_KEY to .env
5. **Run Application**: `streamlit run app.py`
6. **Start Using**: Upload documents and ask questions!

## 🔮 Future Enhancements

- **Multi-user authentication**
- **Collaborative knowledge graphs**
- **Advanced visualization options**
- **Mobile app support**
- **Integration with BinusMaya**
- **Advanced RAG techniques**
- **Automated study plan generation**

This system represents a complete, production-ready Personal Knowledge Graph RAG application that students can use immediately to enhance their learning experience!
