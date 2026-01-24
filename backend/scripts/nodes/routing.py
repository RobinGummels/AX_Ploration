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
        "no_function" if we can skip to query interpretation
    """
    needs_function = state.get("needs_building_function", False)
    
    if needs_function:
        return "needs_function"
    return "no_function"


def route_query_type(state: AgentState) -> Literal["district", "statistics"]:
    """
    Router: Route to appropriate Cypher generator based on query type.
    
    Args:
        state: Current agent state with 'query_type'
        
    Returns:
        The query type for routing to the correct generator
    """
    query_type = state.get("query_type", "district")
    
    # Only district and statistics are valid now
    # (nearby and custom_area have been removed)
    valid_types = ["district", "statistics"]
    
    if query_type in valid_types:
        return query_type
    
    # Default to district if unknown type
    return "district"
