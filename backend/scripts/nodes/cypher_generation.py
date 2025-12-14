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
    
    prompt = PROMPTS[prompt_key]
    
    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"].format(
            query=query,
            attributes=attributes,
            building_functions=building_functions
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


def generate_cypher_nearby(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate Cypher for proximity/radius queries.
    
    Searches for buildings near given coordinates or landmarks.
    """
    return _generate_cypher(state, "cypher_nearby")


def generate_cypher_custom(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate Cypher for custom area queries.
    
    Searches for buildings within user-defined polygons or bounding boxes.
    """
    return _generate_cypher(state, "cypher_custom")


def generate_cypher_stats(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate Cypher for statistical queries.
    
    Generates aggregation queries (count, avg, sum, etc.)
    """
    return _generate_cypher(state, "cypher_statistics")
