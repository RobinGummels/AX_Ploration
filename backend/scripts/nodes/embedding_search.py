"""Node for semantic search on building functions using embeddings."""

from typing import Dict, Any, List

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.neo4j_client import neo4j_client
from ..config import OPENAI_EMBEDDING_MODEL

# Configuration for embedding search filtering
# Adjust these to fine-tune the embedding search behavior
EMBEDDING_SEARCH_CONFIG = {
    # Method: "top_k" (return top N results) or "threshold" (return all above score threshold)
    # or "relative_top1" (return all with score >= best - relative_delta)
    "method": "relative_top1",
    
    # For "top_k" method: number of results to return
    "top_k": 300,
    
    # For "threshold" method: minimum similarity score (0.0 to 1.0)
    "score_threshold": 0.35,

    # For "relative_top1" method: accept results within delta of best score
    "relative_delta": 0.05,
    
    # Show detailed scores in messages
    "show_scores": True,
}


def embedding_search(state: AgentState) -> Dict[str, Any]:
    """
    Node: Search for matching building functions using embeddings.
    
    Creates an embedding of the extracted building function query
    and searches for similar building functions in Neo4j.
    Falls back to basic text search if vector index is not available.
    
    Uses the embedding model specified in OPENAI_EMBEDDING_MODEL config
    to determine whether to use small or large embeddings.
    
    Filtering behavior can be controlled via EMBEDDING_SEARCH_CONFIG:
    - "top_k" method: Returns top N results (default: top 5)
    - "threshold" method: Returns all results above score threshold (default: 0.6)
    
    Args:
        state: Current agent state with 'building_function_query'
        
    Returns:
        Dict with updates for 'building_functions', 'building_function_names', 
        'building_function_descriptions', and 'building_function_scores'
    """
    # Use extracted building function query instead of full query
    building_function_query = state.get("building_function_query", state["query"])
    
    # Determine which embedding model is being used
    use_large_model = "large" in OPENAI_EMBEDDING_MODEL.lower()
    
    # Determine how many results to query (always get top_k from DB, then filter)
    db_top_k = max(300, EMBEDDING_SEARCH_CONFIG.get("top_k", 5))
    
    try:
        # First try vector similarity search
        embedding = llm_client.create_embedding(building_function_query)
        
        results = neo4j_client.similarity_search(
            embedding=embedding,
            top_k=db_top_k,
            use_large_model=use_large_model
        )
        
        if results:
            # Filter results based on configuration
            filtered_results = _filter_results(results)
            
            if filtered_results:
                codes = [r["code"] for r in filtered_results]
                names = [r["name"] for r in filtered_results]
                descriptions = [r["description"] for r in filtered_results]
                scores = [r.get("score", 0.0) for r in filtered_results]
                
                message = _format_message(codes, names, scores)
                
                return {
                    "building_functions": codes,
                    "building_function_names": names,
                    "building_function_descriptions": descriptions,
                    "building_function_scores": scores,
                    "messages": [message]
                }

            # Vector search returned results, but none passed the filter.
            threshold = EMBEDDING_SEARCH_CONFIG.get("score_threshold", 0.6)
            best_score = results[0].get("score", 0.0) if results else 0.0
            return {
                "building_functions": [],
                "building_function_names": [],
                "building_function_descriptions": [],
                "building_function_scores": [],
                "messages": [f"No embedding results above threshold {threshold}. Best score was {best_score:.3f}."]
            }

        # Vector search returned no candidates at all
        return {
            "building_functions": [],
            "building_function_names": [],
            "building_function_descriptions": [],
            "building_function_scores": [],
            "messages": ["No embedding results returned from vector index"]
        }
            
    except Exception as e:
        # Vector search failed (index might not exist), try fallback
        error_msg = str(e)
        
        # Check if it's a "no vector index" error - use fallback, but keep the error message
        if "no such vector" in error_msg.lower() or "vector schema index" in error_msg.lower() or "index" in error_msg.lower():
            fallback_result = _fallback_function_search(building_function_query)
            fallback_result["messages"].append(f"Vector search failed (index): {error_msg}")
            return fallback_result
        
        # For other errors, still try fallback but log the error
        fallback_result = _fallback_function_search(building_function_query)
        fallback_result["messages"].append(f"Vector search failed: {error_msg}")
        return fallback_result


def _filter_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter search results based on EMBEDDING_SEARCH_CONFIG.
    
    Args:
        results: Raw results from similarity_search with scores
        
    Returns:
        Filtered list of results
    """
    method = EMBEDDING_SEARCH_CONFIG.get("method", "top_k")
    
    if method == "threshold":
        # Filter by absolute score threshold
        threshold = EMBEDDING_SEARCH_CONFIG.get("score_threshold", 0.6)
        filtered = [r for r in results if r.get("score", 0.0) >= threshold]
        return filtered

    if method == "relative_top1":
        # Keep all results within delta of the best score
        best_score = results[0].get("score", 0.0) if results else 0.0
        delta = EMBEDDING_SEARCH_CONFIG.get("relative_delta", 0.05)
        threshold = max(0.0, best_score - delta)
        filtered = [r for r in results if r.get("score", 0.0) >= threshold]
        return filtered
    
    elif method == "top_k":
        # Return top K results
        top_k = EMBEDDING_SEARCH_CONFIG.get("top_k", 5)
        return results[:top_k]
    
    else:
        # Default: return top 5
        return results[:5]


def _format_message(codes: List[int], names: List[str], scores: List[float]) -> str:
    """
    Format a human-readable message about found building functions with scores.
    
    Args:
        codes: List of function codes
        names: List of function names
        scores: List of similarity scores
        
    Returns:
        Formatted message string
    """
    if not codes:
        return "No building functions found via embedding"
    
    show_scores = EMBEDDING_SEARCH_CONFIG.get("show_scores", True)
    
    if show_scores and scores:
        # Format with scores
        items = []
        for code, name, score in zip(codes, names, scores):
            items.append(f"{code} ({name}, score: {score:.3f})")
        
        method = EMBEDDING_SEARCH_CONFIG.get("method", "top_k")
        if method == "threshold":
            threshold = EMBEDDING_SEARCH_CONFIG.get("score_threshold", 0.6)
            return f"Found {len(codes)} building functions above threshold {threshold}: {', '.join(items)}"
        if method == "relative_top1":
            delta = EMBEDDING_SEARCH_CONFIG.get("relative_delta", 0.05)
            return f"Found {len(codes)} building functions within {delta} of top score: {', '.join(items)}"
        return f"Found building functions via embedding: {', '.join(items)}"
    else:
        # Format without scores
        return f"Found building functions via embedding: {codes} ({names})"


def _fallback_function_search(query: str) -> Dict[str, Any]:
    """
    Fallback: Search building functions using text matching.
    
    Used when vector index is not available.
    Returns codes, names, descriptions, and scores (all 1.0 for keyword matches).
    """
    try:
        # Get all building functions from database
        all_functions = neo4j_client.get_building_functions()
        
        if not all_functions:
            return {
                "building_functions": [],
                "building_function_names": [],
                "building_function_descriptions": [],
                "building_function_scores": [],
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
            # Fallback matches get perfect score
            scores = [1.0] * len(codes)
            
            return {
                "building_functions": codes,
                "building_function_names": names,
                "building_function_descriptions": descriptions,
                "building_function_scores": scores,
                "messages": [f"Found building functions via keyword matching (fallback): {codes} ({names})"]
            }
        
        # No keyword match - return empty but don't error
        return {
            "building_functions": [],
            "building_function_names": [],
            "building_function_descriptions": [],
            "building_function_scores": [],
            "messages": ["No specific building function identified, proceeding without filter"]
        }
        
    except Exception as e:
        return {
            "building_functions": [],
            "building_function_names": [],
            "building_function_descriptions": [],
            "building_function_scores": [],
            "messages": [f"Fallback function search failed: {str(e)}, proceeding without filter"]
        }
