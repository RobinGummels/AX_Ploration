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
    - nearby: Proximity/radius search
    - custom_area: Custom polygon/area search
    - statistics: Aggregation queries
    
    Args:
        state: Current agent state
        
    Returns:
        Dict with 'query_type' classification
    """
    query = state["query"]
    attributes = state.get("attributes", [])
    building_functions = state.get("building_functions", [])
    
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
