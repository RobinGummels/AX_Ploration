from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from ..config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE


class Neo4jClient:
    """Client for interacting with Neo4j database."""
    
    _instance: Optional["Neo4jClient"] = None
    
    def __new__(cls):
        """Singleton pattern to reuse driver connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._driver = None
        return cls._instance
    
    def __init__(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
    
    def close(self):
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    @contextmanager
    def session(self):
        """Context manager for Neo4j sessions."""
        session = self._driver.session(database=NEO4J_DATABASE)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(self, cypher: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results as list of dicts."""
        with self.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]
    
    def verify_connection(self) -> bool:
        """Verify that the database connection works."""
        try:
            with self.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            return False
    
    def get_building_functions(self) -> List[Dict[str, Any]]:
        """Retrieve all building functions from the database."""
        query = """
        MATCH (f:Function)
        RETURN f.code AS code, 
               f.name AS name,
               f.description AS description
        ORDER BY f.code
        """
        return self.execute_query(query)
    
    def similarity_search(
        self, 
        embedding: List[float], 
        top_k: int = 5,
        use_large_model: bool = False
    ) -> List[Dict[str, Any]]:
        """Perform similarity search on building function embeddings.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            use_large_model: If True, use description_embedding_large, else description_embedding_small
        """
        # Determine which embedding property to use based on model
        index_name = "function_embeddings_large" if use_large_model else "function_embeddings_small"
        
        query = """
        CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
        YIELD node, score
        RETURN node.code AS code,
               node.name AS name,
               node.description AS description,
               score
        ORDER BY score DESC
        """
        try:
            return self.execute_query(query, {
                "index_name": index_name,
                "top_k": top_k,
                "embedding": embedding
            })
        except Exception as e:
            # Fallback: if vector index is missing, do a cosine similarity scan on the embedding property
            error_text = str(e)
            if "no such vector" in error_text.lower() or "vector schema index" in error_text.lower():
                prop = "description_embedding_large" if use_large_model else "description_embedding_small"
                fallback_query = f"""
                MATCH (f:Function)
                WHERE f.{prop} IS NOT NULL
                WITH f, gds.similarity.cosine(f.{prop}, $embedding) AS score
                RETURN f.code AS code,
                       f.name AS name,
                       f.description AS description,
                       score
                ORDER BY score DESC
                LIMIT $top_k
                """
                return self.execute_query(fallback_query, {
                    "embedding": embedding,
                    "top_k": top_k
                })
            raise


# Global instance for convenience
neo4j_client = Neo4jClient()