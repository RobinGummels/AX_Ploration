"""Node for executing Cypher queries against Neo4j."""

from typing import Dict, Any, List

from ..models import AgentState
from ..utils.neo4j_client import neo4j_client


def execute_query(state: AgentState) -> Dict[str, Any]:
    """
    Node: Execute the generated Cypher query against Neo4j.
    
    Takes the Cypher query from state and runs it against the database,
    returning the results.
    
    Args:
        state: Current agent state with 'cypher_query'
        
    Returns:
        Dict with query 'results' or error information
    """
    cypher_query = state.get("cypher_query", "")
    
    if not cypher_query:
        return {
            "results": [],
            "error": "No Cypher query to execute",
            "messages": ["Error: No Cypher query available to execute"]
        }
    
    try:
        # Execute the query
        results = neo4j_client.execute_query(cypher_query)
        
        result_count = len(results)
        
        return {
            "results": results,
            "messages": [f"Query executed successfully, returned {result_count} results"]
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Check for common Cypher errors
        if "SyntaxError" in error_msg:
            return {
                "results": [],
                "error": f"Cypher syntax error: {error_msg}",
                "messages": [f"Cypher syntax error: {error_msg}"]
            }
        elif "Unknown" in error_msg and "label" in error_msg.lower():
            return {
                "results": [],
                "error": f"Unknown label in query: {error_msg}",
                "messages": [f"Unknown label in query: {error_msg}"]
            }
        else:
            return {
                "results": [],
                "error": f"Query execution error: {error_msg}",
                "messages": [f"Query execution error: {error_msg}"]
            }
