"""Nodes for generating Cypher queries based on query type."""

from typing import Dict, Any

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.prompts import PROMPTS


def _generate_cypher(state: AgentState, prompt_key: str) -> Dict[str, Any]:
    """
    Helper function to generate Cypher queries using LLM.
    
    Args:
        state: Current agent state
        prompt_key: Key in PROMPTS dict for the specific query type
        
    Returns:
        Dict with generated 'cypher_query'
    """
    query = state["query"]
    attributes = state.get("attributes", [])
    building_functions = state.get("building_functions", [])
    building_function_names = state.get("building_function_names", [])
    
    # Create a combined representation of functions (code + name) for better prompt context
    if building_functions and building_function_names and len(building_functions) == len(building_function_names):
        functions_text = ", ".join([f"{code} ({name})" for code, name in zip(building_functions, building_function_names)])
    elif building_functions:
        functions_text = ", ".join([str(code) for code in building_functions])
    else:
        functions_text = "[]"
    
    prompt = PROMPTS[prompt_key]
    
    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"].format(
            query=query,
            attributes=attributes,
            building_functions=functions_text
        )}
    ]
    
    try:
        cypher = llm_client.chat_completion(messages)
        
        # Clean up the response (remove markdown code blocks if present)
        cypher = cypher.strip()
        if cypher.startswith("```"):
            lines = cypher.split("\n")
            # Remove first and last line (code block markers)
            cypher = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        
        return {
            "cypher_query": cypher.strip(),
            "messages": [f"Generated Cypher query for {prompt_key}"]
        }
        
    except Exception as e:
        return {
            "cypher_query": "",
            "error": f"Error generating Cypher: {str(e)}",
            "messages": [f"Error generating Cypher: {str(e)}"]
        }


def generate_cypher_district(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate Cypher for district-based queries.
    
    Searches for buildings within districts of Berlin
    (Pankow, Mitte, Friedrichshain-Kreuzberg, etc.)
    """
    return _generate_cypher(state, "cypher_district")
