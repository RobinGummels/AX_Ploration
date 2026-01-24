"""Node for interpreting and classifying user queries."""

from typing import Dict, Any

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.prompts import PROMPTS


def interpret_query(state: AgentState) -> Dict[str, Any]:
    """
    Node: Classify the query type for appropriate processing.
    
    Determines whether the query is:
    - district: Search in administrative areas
    - nearby: Proximity/radius search (only if no spatial_filter provided)
    - custom_area: Custom polygon/area search (only if no spatial_filter provided)
    - statistics: Aggregation queries
    
    If spatial_filter is provided, defaults to 'statistics' to generate a simple
    query without spatial logic. Spatial filtering will be handled by spatial_filtering node.
    
    Args:
        state: Current agent state
        
    Returns:
        Dict with 'query_type' classification
    """
    query = state["query"]
    attributes = state.get("attributes", [])
    building_functions = state.get("building_functions", [])
    spatial_filter = state.get("spatial_filter")
    
    # If spatial_filter is provided, use 'district' query type
    # This generates a simple Cypher query without spatial logic
    # Spatial filtering will be handled by spatial_filtering node
    if spatial_filter:
        return {
            "query_type": "district",
            "messages": [f"Query type: district (spatial filtering will be applied via spatial_filter parameter)"]
        }
    
    prompt = PROMPTS["interpret_query"]
    
    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"].format(
            query=query,
            attributes=attributes,
            building_functions=building_functions
        )}
    ]
    
    try:
        response = llm_client.chat_completion_json(messages)
        
        query_type = response.get("query_type", "district")
        reasoning = response.get("reasoning", "")
        
        return {
            "query_type": query_type,
            "messages": [f"Query type: {query_type} ({reasoning})"]
        }
        
    except Exception as e:
        # Default to district if classification fails
        return {
            "query_type": "district",
            "error": f"Error in query interpretation: {str(e)}",
            "messages": [f"Error in query interpretation, defaulting to 'district': {str(e)}"]
        }
