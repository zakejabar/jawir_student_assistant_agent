 
"""
Hybrid Query Engine: Vector similarity + Graph traversal for personal RAG
"""
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import streamlit as st
from config.llm_config import llm_config
from src.neo4j_client import neo4j_client
from src.agent.agent_structurer import build_structured_context
from src.agent.answer_generator import generate_answer

class QueryEngine:
    def __init__(self):
        self.llm = llm_config.get_llm()
        
        # Initialize sentence transformer for embeddings (cached)
        @st.cache_resource
        def get_embedding_model():
            return SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
        
        self.embedding_model = get_embedding_model()
        
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        if not texts:
            return np.array([])
        return self.embedding_model.encode(texts, convert_to_tensor=False)
    
    def store_document_embeddings(self, user_id: str, document_text: str, chunk_id: str):
        """
        Store document chunk with embeddings for vector search
        
        In a production system, you'd want a proper vector database.
        For demo, we'll use in-memory storage with Neo4j properties.
        """
        # This is a simplified approach
        # In production, use: Pinecone, Weaviate, ChromaDB, etc.
        embedding = self.encode_texts([document_text])[0]
        

        # Store chunk as Neo4j node with embedding (as string for demo)
        with neo4j_client.driver.session() as session:
            session.run(
                f"""
                MERGE (c:Chunk:User_{user_id} {{id: $chunk_id}})
                SET c.text = $text,
                    c.embedding = $embedding,
                    c.user_id = $user_id
                """,
                chunk_id=chunk_id,
                text=document_text,  # Store first 1000 chars
                embedding=json.dumps(embedding.tolist()),
                user_id=user_id
            )
    
    def vector_search(self, query: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search on user's documents
        
        Args:
            query: Search query
            user_id: User identifier
            top_k: Number of results to return
            
        Returns:
            List of relevant document chunks
        """

        # Get user's document chunks from Neo4j
        with neo4j_client.driver.session() as session:
            result = session.run(
                f"""
                MATCH (c:Chunk:User_{user_id})
                RETURN c.id as id, c.text as text
                """,
                user_id=user_id
            )
            
            chunks = [{"id": record["id"], "text": record["text"]} for record in result]
        
        if not chunks:
            return []
        
        # Encode query and document chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        query_embedding = self.encode_texts([query])[0]
        chunk_embeddings = self.encode_texts(chunk_texts)
        
        # Calculate cosine similarities
        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                results.append({
                    "chunk": chunks[idx],
                    "similarity": float(similarities[idx])
                })
        
        return results
    
    def get_graph_context(self, concept: str, user_id: str, depth: int = 2):
        with neo4j_client.driver.session() as session:
            result = session.run(
                f"""
                MATCH (c:Entity:User_{user_id} {{name: $concept}})
                OPTIONAL MATCH (c)-[r]->(n)
                RETURN c, r, n
                """,
                concept=concept
            )

            entities = set()
            relationships = []

            for record in result:
                if record["c"]:
                    entities.add((record["c"]["name"], record["c"]["type"]))
                if record["n"]:
                    entities.add((record["n"]["name"], record["n"]["type"]))
                if record["r"]:
                    relationships.append({
                        "from": record["c"]["name"],
                        "to": record["n"]["name"],
                        "type": record["r"]["type"]
                    })

        return {
            "entities": [{"name": e[0], "type": e[1]} for e in entities],
            "relationships": relationships
        }
    
    def extract_main_concept(self, question: str) -> Optional[str]:
        prompt = f"""
        Extract the main academic concept from this question.
        Return ONLY the concept name.

        Question: {question}
        """

        response = self.llm.invoke(prompt)
        return response.content.strip()
    
    def generate_answer(self, question: str, user_id: str):

        concept = self.extract_main_concept(question)
        graph_context = self.get_graph_context(concept, user_id)

        if not graph_context["entities"]:
            return {
                "answer": "I could not find this topic in your uploaded materials.",
                "success": False
            }

        vector_results = self.vector_search(concept, user_id)

        structured_context = build_structured_context(
            graph_context,
            vector_results
        )

        prompt = generate_answer(question, structured_context)
        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "success": True
        }

# Global query engine instance
query_engine = QueryEngine()
