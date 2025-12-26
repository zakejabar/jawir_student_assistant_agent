"""
BinusBrain - Personal Knowledge Graph RAG System
Main Streamlit Application
"""
import streamlit as st
import os
from datetime import datetime

# Import our custom modules
from src.agent import agent as binus_agent
from src.graph_viz import graph_visualizer
from config.neo4j_config import neo4j_config
from config.llm_config import llm_config

# Configure Streamlit page
st.set_page_config(
    page_title="mamatbinbudi - Personal Knowledge Graph",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .chat-section {
        background-color: #e8f4fd;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .viz-section {
        background-color: #f3e5f5;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-msg {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        # In production, use proper authentication
        st.session_state.user_id = f"student_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

def check_dependencies():
    """Check if all dependencies are configured"""
    issues = []
    
    # Check Neo4j connection
    if not neo4j_config.test_connection():
        issues.append("❌ Neo4j connection failed. Please start Neo4j and check credentials.")
    
    # Check OpenRouter API key
    if not os.getenv("OPENROUTER_API_KEY"):
        issues.append("❌ OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file.")
    
    # Test LLM connection
    try:
        llm_config.test_connection()
    except Exception as e:
        issues.append(f"❌ LLM connection failed: {str(e)}")
    
    return issues

def render_header():
    """Render the application header"""
    st.title("🧠 mamatbinbudi")
    st.markdown("### Personal Knowledge Graph RAG System")
    st.markdown("---")
    
    # User info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**👤 User ID:** `{st.session_state.user_id}`")
    with col2:
        st.markdown(f"**📁 Files Uploaded:** {len(st.session_state.uploaded_files)}")
    with col3:
        st.markdown(f"**💬 Chat Messages:** {len(st.session_state.chat_history)}")

def render_upload_section():
    """Render file upload section"""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📁 Upload Materials")
    st.markdown("Upload your documents (PDF, TXT, or Images) to build your personal knowledge graph.")
    

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'png', 'jpg', 'jpeg', 'pptx'],
        help="Supported formats: PDF, TXT, PNG, JPG, JPEG, PPTX (PowerPoint)"
    )
    
    if uploaded_file is not None:
        st.markdown(f"**📄 Selected:** {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        if st.button("🚀 Process & Index", type="primary"):
            with st.spinner("Processing file..."):
                try:
                    # Read file data
                    file_data = uploaded_file.read()
                    
                    # Process with agent
                    result = binus_agent.upload(
                        user_id=st.session_state.user_id,
                        file_data=file_data,
                        filename=uploaded_file.name
                    )
                    
                    if result.get("success"):
                        # Update session state
                        st.session_state.uploaded_files.append({
                            "name": uploaded_file.name,
                            "size": uploaded_file.size,
                            "type": result.get("file_type", "unknown"),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # Show success message
                        st.markdown(f"""
                        <div class="success-msg">
                            ✅ <strong>Success!</strong> File processed successfully.<br>
                            📊 Entities extracted: {result.get('processing_result', {}).get('total_entities', 0)}<br>
                            🔗 Relationships created: {result.get('processing_result', {}).get('total_relationships', 0)}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show processing details
                        if "messages" in result:
                            for msg in result["messages"]:
                                if hasattr(msg, 'content'):
                                    st.info(msg.content)
                        
                    else:
                        st.markdown(f"""
                        <div class="error-msg">
                            ❌ <strong>Error:</strong> {result.get('error', 'Unknown error')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-msg">
                        ❌ <strong>Exception:</strong> {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_section():
    """Render chat query section"""
    st.markdown('<div class="chat-section">', unsafe_allow_html=True)
    st.markdown("### 💬 Ask Questions About Your Materials")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("#### 📜 Chat History")
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            with st.expander(f"Q{i+1}: {question[:50]}..."):
                st.markdown(f"**Question:** {question}")
                st.markdown(f"**Answer:** {answer}")
    
    # Question input
    question = st.text_input(
        "Ask a question about your uploaded materials:",
        placeholder="e.g., What are the main concepts in my documents?",
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary")
    with col2:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    if ask_button and question:
        with st.spinner("Generating answer..."):
            try:
                # Query with agent
                result = binus_agent.ask(
                    user_id=st.session_state.user_id,
                    question=question
                )
                
                if result.get("success"):
                    answer = result.get("query_result", {}).get("answer", "No answer generated")
                    
                    # Add to chat history
                    st.session_state.chat_history.append((question, answer))
                    
                    # Display answer
                    st.markdown("#### 🎯 Answer")
                    st.markdown(answer)
                    
                    # Show context if available
                    context = result.get("query_result", {}).get("context", {})
                    if context:
                        st.markdown("#### 📊 Query Context")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Documents Found", context.get("documents_found", 0))
                        with col2:
                            st.metric("Graph Entities", context.get("graph_entities", 0))
                        with col3:
                            st.metric("Relationships", context.get("graph_relationships", 0))
                else:
                    st.markdown(f"""
                    <div class="error-msg">
                        ❌ <strong>Error:</strong> {result.get('error', 'Unknown error')}
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-msg">
                    ❌ <strong>Exception:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_visualization_section():
    """Render knowledge graph visualization section"""
    st.markdown('<div class="viz-section">', unsafe_allow_html=True)
    st.markdown("### 🕸️ Knowledge Graph Visualization")
    st.markdown("Explore your personal knowledge graph built from your uploaded materials.")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        visualize_button = st.button("🎨 Visualize Graph", type="primary")
    with col2:

        if st.button("📊 Export Graph Data"):
            try:
                export_data = graph_visualizer.export_graph_data(st.session_state.user_id)
                if export_data["success"]:
                    # Convert to JSON string for download
                    import json
                    json_data = json.dumps(export_data, indent=2, default=str)
                    
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_data,
                        file_name=f"binusbrain_graph_{st.session_state.user_id}.json",
                        mime="application/json"
                    )
                    
                    st.success(f"✅ Export ready! {export_data['statistics']['nodes']} nodes, {export_data['statistics']['edges']} relationships")
                else:
                    st.error(f"Export failed: {export_data.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Export error: {str(e)}")
    
    if visualize_button:
        with st.spinner("Generating knowledge graph..."):
            try:
                graph_visualizer.render_graph_in_streamlit(st.session_state.user_id)
            except Exception as e:
                st.markdown(f"""
                <div class="error-msg">
                    ❌ <strong>Visualization Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with controls and info"""
    with st.sidebar:
        st.markdown("## 🔧 System Status")
        
        # Check dependencies
        issues = check_dependencies()
        
        if not issues:
            st.markdown("✅ All systems operational")
        else:
            for issue in issues:
                st.markdown(issue)
        
        st.markdown("---")
        
        # User management
        st.markdown("## 👤 User Management")
        
        if st.button("🔄 New User Session"):
            st.session_state.user_id = f"student_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.chat_history = []
            st.session_state.uploaded_files = []
            st.rerun()
        
        st.markdown(f"**Current User:** `{st.session_state.user_id}`")
        
        # Quick stats
        st.markdown("---")
        st.markdown("## 📊 Quick Stats")
        st.metric("Files Uploaded", len(st.session_state.uploaded_files))
        st.metric("Chat Messages", len(st.session_state.chat_history))
        
        # Help section
        st.markdown("---")
        st.markdown("## ❓ Help")

        st.markdown("""
        **How to use:**
        1. Upload your documents (PDF, TXT, images, PowerPoint)
        2. Ask questions about your materials
        3. Visualize your knowledge graph
        
        **Supported formats:**
        - 📄 PDF files
        - 📝 Text files (.txt)
        - 🖼️ Images (PNG, JPG)
        - 📊 PowerPoint files (.pptx)
        """)

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Create main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main content area
        render_upload_section()
        render_chat_section()
        render_visualization_section()
    
    with col2:
        # Sidebar
        render_sidebar()

if __name__ == "__main__":
    main()
