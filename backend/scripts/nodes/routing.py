"""Routing functions for conditional edges in the workflow graph."""

from typing import Literal

from ..models import AgentState


def route_function_needed(state: AgentState) -> Literal["needs_function", "no_function"]:
    """
    Router: Determine if building function lookup is needed.
    
    Based on the attribute identification step, decides whether
    to perform an embedding search for building functions.
    
    Args:
        state: Current agent state
        
    Returns:
        "needs_function" if embedding search is needed
        "no_function" if we can skip directly to Cypher generation
    """
    needs_function = state.get("needs_building_function", False)
    
    if needs_function:
        return "needs_function"
    return "no_function"
