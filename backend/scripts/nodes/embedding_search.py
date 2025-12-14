"""Node for semantic search on building functions using embeddings."""

from typing import Dict, Any

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.neo4j_client import neo4j_client


def embedding_search(state: AgentState) -> Dict[str, Any]:
    """
    Node: Search for matching building functions using embeddings.
    
    Creates an embedding of the user's building function hint
    and searches for similar building functions in Neo4j.
    Falls back to basic text search if vector index is not available.
    
    Args:
        state: Current agent state with building function hint
        
    Returns:
        Dict with updates for 'building_functions' and 'building_function_descriptions'
    """
    query = state["query"]
    
    try:
        # First try vector similarity search
        embedding = llm_client.create_embedding(query)
        
        results = neo4j_client.similarity_search(
            embedding=embedding,
            top_k=5,
            index_name="building_function_embeddings"
        )
        
        if results:
            codes = [r["code"] for r in results]
            descriptions = [r["description"] for r in results]
            
            return {
                "building_functions": codes,
                "building_function_descriptions": descriptions,
                "messages": [f"Found building functions via embedding: {codes}"]
            }
            
    except Exception as e:
        # Vector search failed (index might not exist), try fallback
        error_msg = str(e)
        
        # Check if it's a "no vector index" error - use fallback
        if "no such vector" in error_msg.lower() or "vector schema index" in error_msg.lower():
            return _fallback_function_search(query)
        
        # For other errors, still try fallback but log the error
        fallback_result = _fallback_function_search(query)
        fallback_result["messages"].append(f"Vector search failed: {error_msg}")
        return fallback_result
    
    # No results from vector search, try fallback
    return _fallback_function_search(query)

    # TODO: Remove temporary fallback once vector index is reliably set up
def _fallback_function_search(query: str) -> Dict[str, Any]:
    """
    Fallback: Search building functions using text matching.
    
    Used when vector index is not available.
    """
    try:
        # Get all building functions from database
        all_functions = neo4j_client.get_building_functions()
        
        if not all_functions:
            return {
                "building_functions": [],
                "building_function_descriptions": [],
                "messages": ["No building functions found in database"]
            }
        
        # Simple keyword matching
        query_lower = query.lower()
        keywords = {
            "wohn": ["1000", "1010", "1020", "1100"],  # Wohngebäude
            "büro": ["2000", "2010"],  # Bürogebäude
            "industrie": ["2500", "2510"],  # Industriegebäude
            "schule": ["3000", "3010"],  # Schulen
            "kirche": ["3200"],  # Kirchen
            "krankenhaus": ["3100"],  # Krankenhäuser
            "hotel": ["2100"],  # Hotels
            "geschäft": ["2300"],  # Geschäftsgebäude
            "landwirtschaft": ["2700"],  # Landwirtschaft
        }
        
        matched_codes = []
        for keyword, codes in keywords.items():
            if keyword in query_lower:
                matched_codes.extend(codes)
        
        if matched_codes:
            # Filter functions that match our codes
            matched_functions = [f for f in all_functions if f.get("code") in matched_codes]
            codes = [f["code"] for f in matched_functions]
            descriptions = [f.get("description", "") for f in matched_functions]
            
            return {
                "building_functions": codes,
                "building_function_descriptions": descriptions,
                "messages": [f"Found building functions via keyword matching: {codes}"]
            }
        
        # No keyword match - return empty but don't error
        return {
            "building_functions": [],
            "building_function_descriptions": [],
            "messages": ["No specific building function identified, proceeding without filter"]
        }
        
    except Exception as e:
        return {
            "building_functions": [],
            "building_function_descriptions": [],
            "messages": [f"Fallback function search failed: {str(e)}, proceeding without filter"]
        }
