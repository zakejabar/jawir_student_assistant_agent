"""
Neo4j client for direct graph operations
"""
import json
from typing import List, Dict, Any, Optional
from config.neo4j_config import neo4j_config

class Neo4jClient:
    def __init__(self):
        self.driver = neo4j_config.get_driver()
        
    def close(self):
        """Close Neo4j driver"""
        if self.driver:
            self.driver.close()
    
    def create_user_if_not_exists(self, user_id: str):
        """Create user node if it doesn't exist"""
        with self.driver.session() as session:
            session.run(
                "MERGE (u:User {id: $user_id})",
                user_id=user_id
            )
    

    def create_entities(self, entities: List[Dict[str, str]], user_id: str):
        """Create entity nodes with user isolation"""
        with self.driver.session() as session:
            for entity in entities:
                session.run(
                    f"""
                    MERGE (e:Entity:User_{user_id} {{name: $name}})
                    SET e.type = $type,
                        e.user_id = $user_id,
                        e.created_at = datetime()
                    """,
                    name=entity["name"],
                    type=entity.get("type", "concept"),
                    user_id=user_id
                )
    

    def create_relationships(self, relationships: List[Dict[str, str]], user_id: str):
        """Create relationship edges with user isolation"""
        with self.driver.session() as session:
            for rel in relationships:
                session.run(
                    f"""
                    MATCH (a:Entity:User_{user_id} {{name: $from_entity}})
                    MATCH (b:Entity:User_{user_id} {{name: $to_entity}})
                    MERGE (a)-[r:RELATES {{
                        type: $rel_type,
                        user_id: $user_id,
                        created_at: datetime()
                    }}]->(b)
                    """,
                    from_entity=rel["from"],
                    to_entity=rel["to"],
                    rel_type=rel.get("type", "relates_to"),
                    user_id=user_id
                )
    

    def get_user_entities(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's entities"""
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (e:Entity:User_{user_id})
                RETURN e.name as name, e.type as type, e.user_id as user_id
                ORDER BY e.created_at DESC
                LIMIT $limit
                """,
                user_id=user_id,
                limit=limit
            )
            return [dict(record) for record in result]
    

    def get_user_relationships(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's relationships"""
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (a:Entity:User_{user_id})-[r:RELATES]->(b:Entity:User_{user_id})
                RETURN a.name as from_entity, b.name as to_entity, r.type as rel_type
                ORDER BY r.created_at DESC
                LIMIT $limit
                """,
                user_id=user_id,
                limit=limit
            )
            return [dict(record) for record in result]
    

    def get_user_graph_data(self, user_id: str) -> Dict[str, Any]:
        """Get complete graph data for visualization"""
        with self.driver.session() as session:
            # Get entities
            entities_result = session.run(
                f"MATCH (e:Entity:User_{user_id}) RETURN e.name as id, e.type as type",
                user_id=user_id
            )
            entities = [{"id": record["id"], "label": record["id"], "type": record["type"]} 
                       for record in entities_result]
            
            # Get relationships
            rels_result = session.run(
                f"""
                MATCH (a:Entity:User_{user_id})-[r:RELATES]->(b:Entity:User_{user_id})
                RETURN a.name as from, b.name as to, r.type as label
                """,
                user_id=user_id
            )
            relationships = [{"from": record["from"], "to": record["to"], "label": record["label"]}
                           for record in rels_result]
            
            return {"nodes": entities, "edges": relationships}
    

    def delete_user_data(self, user_id: str):
        """Delete all user data (for testing/reset)"""
        with self.driver.session() as session:
            session.run(
                f"""
                MATCH (e:Entity:User_{user_id})
                DETACH DELETE e
                """,
                user_id=user_id
            )

    def get_framework_by_name(self, name: str):
        query = """
        MATCH (f:Entity {type: 'framework'})
        WHERE toLower(f.name) CONTAINS toLower($name)
        RETURN f.name AS name
        """
        return self.run(query, {"name": name})

    def get_components_of_framework(self, framework_name: str):
        query = """
        MATCH (f:Entity {name: $framework})-[:HAS_COMPONENT]->(c)
        RETURN c.name AS name, c.type AS type
        """
        return self.run(query, {"framework": framework_name})

# Global client instance
neo4j_client = Neo4jClient()
