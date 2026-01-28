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
            "results": [{"buildings": []}],
            "error": "No Cypher query to execute",
            "messages": ["Error: No Cypher query available to execute"]
        }
    
    try:
        # Execute the query
        results = neo4j_client.execute_query(cypher_query)
        
        # Results are already in the correct format from Neo4j
        # If they're a plain list, wrap them; otherwise pass through
        if isinstance(results, list) and len(results) > 0:
            # Check if already wrapped
            if isinstance(results[0], dict) and "buildings" in results[0]:
                # Already in correct format: [{"buildings": [...]}]
                pass
            else:
                # Plain list of buildings - wrap them
                results = [{"buildings": results}]
        elif not results:
            # Empty results
            results = [{"buildings": []}]
        
        # Count buildings for logging
        building_count = 0
        if isinstance(results, list) and len(results) > 0 and isinstance(results[0], dict):
            building_count = len(results[0].get("buildings", []))
        
        return {
            "results": results,
            "messages": [f"Query executed successfully, returned {building_count} results"]
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Check for common Cypher errors
        if "SyntaxError" in error_msg:
            return {
                "results": [{"buildings": []}],
                "error": f"Cypher syntax error: {error_msg}",
                "messages": [f"Cypher syntax error: {error_msg}"]
            }
        elif "Unknown" in error_msg and "label" in error_msg.lower():
            return {
                "results": [{"buildings": []}],
                "error": f"Unknown label in query: {error_msg}",
                "messages": [f"Unknown label in query: {error_msg}"]
            }
        else:
            return {
                "results": [{"buildings": []}],
                "error": f"Query execution error: {error_msg}",
                "messages": [f"Query execution error: {error_msg}"]
            }
