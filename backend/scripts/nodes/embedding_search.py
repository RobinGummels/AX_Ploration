"""Node for semantic search on building functions using embeddings."""

from typing import Dict, Any

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.neo4j_client import neo4j_client
from ..config import OPENAI_EMBEDDING_MODEL


def embedding_search(state: AgentState) -> Dict[str, Any]:
    """
    Node: Search for matching building functions using embeddings.
    
    Creates an embedding of the user's building function hint
    and searches for similar building functions in Neo4j.
    Falls back to basic text search if vector index is not available.
    
    Uses the embedding model specified in OPENAI_EMBEDDING_MODEL config
    to determine whether to use small or large embeddings.
    
    Args:
        state: Current agent state with building function hint
        
    Returns:
        Dict with updates for 'building_functions', 'building_function_names', 
        and 'building_function_descriptions'
    """
    query = state["query"]
    
    # Determine which embedding model is being used
    use_large_model = "large" in OPENAI_EMBEDDING_MODEL.lower()
    
    try:
        # First try vector similarity search
        embedding = llm_client.create_embedding(query)
        
        results = neo4j_client.similarity_search(
            embedding=embedding,
            top_k=5,
            use_large_model=use_large_model
        )
        
        if results:
            codes = [r["code"] for r in results]
            names = [r["name"] for r in results]
            descriptions = [r["description"] for r in results]
            
            return {
                "building_functions": codes,
                "building_function_names": names,
                "building_function_descriptions": descriptions,
                "messages": [f"Found building functions via embedding: {codes} ({names})"]
            }
            
    except Exception as e:
        # Vector search failed (index might not exist), try fallback
        error_msg = str(e)
        
        # Check if it's a "no vector index" error - use fallback
        if "no such vector" in error_msg.lower() or "vector schema index" in error_msg.lower() or "index" in error_msg.lower():
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
    Returns codes, names, and descriptions.
    """
    try:
        # Get all building functions from database
        all_functions = neo4j_client.get_building_functions()
        
        if not all_functions:
            return {
                "building_functions": [],
                "building_function_names": [],
                "building_function_descriptions": [],
                "messages": ["No building functions found in database"]
            }
        
        # Simple keyword matching
        query_lower = query.lower()
        keywords = {
            "wohn": [1000, 1010, 1020, 1023, 1024],  # Wohngebäude
            "büro": [2020, 1122],  # Bürogebäude
            "industrie": [2100, 2200],  # Industriegebäude
            "schule": [3021, 3022, 3023],  # Schulen
            "kirche": [3041],  # Kirchen
            "krankenhaus": [3051, 3242],  # Krankenhäuser (3051: Krankenhaus, 3242: Sanatorium)
            "hotel": [2071],  # Hotels
            "geschäft": [2050, 2052, 1123],  # Geschäftsgebäude
            "landwirtschaft": [2721, 2726],  # Landwirtschaft
        }
        
        matched_codes = []
        for keyword, codes in keywords.items():
            if keyword in query_lower:
                matched_codes.extend(codes)
        
        if matched_codes:
            # Filter functions that match our codes
            matched_functions = [f for f in all_functions if f.get("code") in matched_codes]
            codes = [f["code"] for f in matched_functions]
            names = [f.get("name", "") for f in matched_functions]
            descriptions = [f.get("description", "") for f in matched_functions]
            
            return {
                "building_functions": codes,
                "building_function_names": names,
                "building_function_descriptions": descriptions,
                "messages": [f"Found building functions via keyword matching: {codes} ({names})"]
            }
        
        # No keyword match - return empty but don't error
        return {
            "building_functions": [],
            "building_function_names": [],
            "building_function_descriptions": [],
            "messages": ["No specific building function identified, proceeding without filter"]
        }
        
    except Exception as e:
        return {
            "building_functions": [],
            "building_function_names": [],
            "building_function_descriptions": [],
            "messages": [f"Fallback function search failed: {str(e)}, proceeding without filter"]
        }
