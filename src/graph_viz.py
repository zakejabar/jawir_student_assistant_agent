"""
Knowledge Graph Visualization using PyVis
"""
import json
from typing import Dict, Any, List
from pyvis.network import Network
import streamlit as st
from src.neo4j_client import neo4j_client

class GraphVisualizer:
    def __init__(self):
        self.colors = {
            'concept': '#FF6B6B',
            'person': '#4ECDC4', 
            'place': '#45B7D1',
            'organization': '#96CEB4',
            'term': '#FFEAA7',
            'definition': '#DDA0DD'
        }
        
        self.default_color = '#B0B0B0'
    


    def create_network_graph(self, graph_data: Dict[str, Any], user_id: str) -> str:
        """
        Create interactive network graph from Neo4j data
        
        Args:
            graph_data: Dictionary with 'nodes' and 'edges' from Neo4j
            user_id: User identifier for title
            
        Returns:
            HTML string for Streamlit rendering
        """
        try:
            # Validate input data
            if not graph_data or not isinstance(graph_data, dict):
                return self._create_error_html("Invalid graph data provided")
            
            # Get nodes and edges safely
            nodes = graph_data.get('nodes', []) or []
            edges = graph_data.get('edges', []) or []
            
            if not nodes:
                return self._create_error_html("No nodes found in graph data")
            
            # Create PyVis network with basic configuration only
            net = Network(height="600px", width="100%")
            
            # Add nodes with safe handling
            node_ids = set()
            nodes_added = 0
            
            for node in nodes:
                try:
                    if not isinstance(node, dict):
                        continue
                        
                    node_id = str(node.get('id', '')).strip()
                    if not node_id or node_id in node_ids:
                        continue
                    node_ids.add(node_id)
                    
                    node_label = str(node.get('label', node_id)).strip()
                    node_type = str(node.get('type', 'concept')).strip()
                    
                    # Ensure valid types for PyVis
                    if not node_label:
                        node_label = node_id
                    
                    # Choose color based on entity type (use string color)
                    color = self.colors.get(node_type, self.default_color)
                    
                    # Calculate node size based on connections
                    node_size = self._calculate_node_size(node_id, edges)
                    
                    # Add node with minimal configuration to avoid PyVis errors
                    net.add_node(
                        node_id,
                        label=node_label[:50] if len(node_label) > 50 else node_label,
                        color=color,
                        size=max(10, min(30, node_size))
                    )
                    nodes_added += 1
                    
                except Exception as e:
                    print(f"Error adding node {node}: {e}")
                    continue
            
            # Add edges with safe handling
            edges_added = 0
            for edge in edges:
                try:
                    if not isinstance(edge, dict):
                        continue
                        
                    from_node = str(edge.get('from', '')).strip()
                    to_node = str(edge.get('to', '')).strip()
                    edge_label = str(edge.get('label', 'relates_to')).strip()
                    
                    # Only add edge if both nodes exist
                    if from_node in node_ids and to_node in node_ids and from_node != to_node:
                        # Add edge with minimal configuration
                        net.add_edge(
                            from_node,
                            to_node
                        )
                        edges_added += 1
                        
                except Exception as e:
                    print(f"Error adding edge {edge}: {e}")
                    continue
            
            if nodes_added == 0:
                return self._create_error_html("No valid nodes could be added to the graph")
            
            # Set very basic options to avoid PyVis configuration issues
            try:
                net.set_options({"physics": {"enabled": True}})
            except Exception as e:
                print(f"Warning: Could not set options: {e}")
                # Continue without custom options
            
            # Generate HTML
            try:
                html_string = net.generate_html()
            except Exception as e:
                return self._create_error_html(f"Failed to generate HTML: {str(e)}")
            
            # Add custom styling and title
            styled_html = f"""
            <div style="background-color: #2E2E2E; padding: 20px; border-radius: 10px;">
                <h3 style="color: white; text-align: center; margin-bottom: 10px;">
                    🕸️ Knowledge Graph for User: {user_id}
                </h3>
                <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                    <p style="color: #CCCCCC; margin: 0; font-size: 14px;">
                        📊 Nodes: {nodes_added} | 
                        🔗 Relationships: {edges_added}
                    </p>
                </div>
                {html_string}
            </div>
            """
            
            return styled_html
            
        except Exception as e:
            print(f"Error creating network graph: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_html(f"Graph creation failed: {str(e)}")
    
    def _create_error_html(self, error_message: str) -> str:
        """Create error HTML display"""
        return f"""
        <div style="background-color: #ffebee; padding: 20px; border-radius: 10px; color: #c62828; text-align: center;">
            <h3>🚫 Graph Visualization Error</h3>
            <p style="font-size: 16px; margin: 10px 0;">{error_message}</p>
            <p style="font-size: 14px; opacity: 0.8;">Please try uploading more documents or check your data.</p>
        </div>
        """
    
    def _calculate_node_size(self, node_id: str, edges: List[Dict[str, Any]]) -> int:
        """Calculate node size based on number of connections"""
        connections = 0
        
        for edge in edges:
            if edge['from'] == node_id or edge['to'] == node_id:
                connections += 1
        
        # Base size + connection bonus
        return max(15, min(40, 15 + connections * 3))
    
    def render_graph_in_streamlit(self, user_id: str):
        """
        Render knowledge graph directly in Streamlit
        
        Args:
            user_id: User identifier
        """
        try:
            # Get graph data from Neo4j
            graph_data = neo4j_client.get_user_graph_data(user_id)
            
            if not graph_data['nodes']:
                st.warning("No knowledge graph data found. Upload some documents first!")
                return
            
            # Create and render network
            html_content = self.create_network_graph(graph_data, user_id)
            
            # Display in Streamlit
            st.components.v1.html(html_content, height=700)
            
            # Add legend
            self._render_legend()
            
            # Add statistics
            self._render_graph_stats(graph_data)
            
        except Exception as e:
            st.error(f"Error rendering graph: {str(e)}")
    
    def _render_legend(self):
        """Render legend for node types and colors"""
        st.markdown("### 📚 Node Types")
        
        cols = st.columns(len(self.colors))
        for i, (node_type, color) in enumerate(self.colors.items()):
            with cols[i]:
                st.markdown(
                    f'<div style="background-color: {color}; width: 20px; height: 20px; '
                    f'display: inline-block; border-radius: 50%; margin-right: 8px;"></div>'
                    f'<span style="color: white;">{node_type.title()}</span>',
                    unsafe_allow_html=True
                )
    
    def _render_graph_stats(self, graph_data: Dict[str, Any]):
        """Render graph statistics"""
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # Calculate statistics
        total_nodes = len(nodes)
        total_edges = len(edges)
        node_types = {}
        
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Display statistics
        st.markdown("### 📈 Graph Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Nodes", total_nodes)
        
        with col2:
            st.metric("Total Relationships", total_edges)
        
        with col3:
            avg_connections = round(total_edges / total_nodes * 2 if total_nodes > 0 else 0, 1)
            st.metric("Avg Connections per Node", avg_connections)
        
        # Node type breakdown
        if node_types:
            st.markdown("**Node Types:**")
            for node_type, count in sorted(node_types.items()):
                st.markdown(f"- {node_type.title()}: {count} nodes")
    
    def export_graph_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export graph data for external use
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with graph data and metadata
        """
        try:
            graph_data = neo4j_client.get_user_graph_data(user_id)
            
            return {
                "user_id": user_id,
                "export_timestamp": "2024-12-13",
                "statistics": {
                    "nodes": len(graph_data.get('nodes', [])),
                    "edges": len(graph_data.get('edges', [])),
                    "node_types": self._get_node_type_counts(graph_data.get('nodes', []))
                },
                "data": graph_data,
                "success": True
            }
            
        except Exception as e:
            return {
                "user_id": user_id,
                "success": False,
                "error": str(e)
            }
    
    def _get_node_type_counts(self, nodes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get counts of node types"""
        type_counts = {}
        for node in nodes:
            node_type = node.get('type', 'unknown')
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return type_counts

# Global visualizer instance
graph_visualizer = GraphVisualizer()
