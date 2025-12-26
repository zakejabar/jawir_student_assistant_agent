"""
Neo4j configuration and connection management
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jConfig:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j") 
        self.password = os.getenv("NEO4J_PASSWORD", "neo4j")
        
    def get_driver(self):
        """Get Neo4j driver instance"""
        return GraphDatabase.driver(
            self.uri, 
            auth=(self.username, self.password)
        )
        
    def test_connection(self):
        """Test Neo4j connection"""
        try:
            driver = self.get_driver()
            driver.verify_connectivity()
            driver.close()
            return True
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            return False

# Global config instance
neo4j_config = Neo4jConfig()
