from typing import Dict, Any

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.prompts import PROMPTS


def identify_attributes(state: AgentState) -> Dict[str, Any]:
    """
    Node: Identify building attributes from user query.
    
    Analyzes the user's query to determine:
    - Which building attributes are being searched for
    - Whether a building function lookup is needed
    
    Args:
        state: Current agent state with 'query' field
        
    Returns:
        Dict with updates for 'attributes', 'needs_building_function', and 'messages'
    """
    query = state["query"]
    prompt = PROMPTS["identify_attributes"]
    
    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"].format(query=query)}
    ]
    
    try:
        response = llm_client.chat_completion_json(messages)
        
        return {
            "attributes": response.get("attributes", []),
            "needs_building_function": response.get("needs_building_function", False),
            "messages": [f"Identified attributes: {response.get('attributes', [])}"]
        }
        
    except Exception as e:
        return {
            "attributes": [],
            "needs_building_function": False,
            "error": f"Error in attribute identification: {str(e)}",
            "messages": [f"Error in attribute identification: {str(e)}"]
        }