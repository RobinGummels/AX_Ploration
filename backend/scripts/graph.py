from langgraph.graph import StateGraph, START, END
from typing import Literal

from .models import AgentState
from .nodes import (
    identify_attributes,
    embedding_search,
    generate_cypher_district,
    execute_query,
    spatial_filtering,
    statistics_calculation,
    generate_answer,
    route_function_needed
)


def create_workflow() -> StateGraph:
    """Create and configure the agent workflow graph."""
    
    workflow = StateGraph(AgentState)
    
    # ===================
    # Add all nodes
    # ===================
    
    # Phase 1: Query Analysis
    workflow.add_node("identify_attributes", identify_attributes)
    workflow.add_node("embedding_search", embedding_search)
    
    # Phase 2: Cypher Generation
    workflow.add_node("generate_cypher_district", generate_cypher_district)
    
    # Phase 3: Data Retrieval & Processing
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("spatial_filtering", spatial_filtering)
    workflow.add_node("statistics_calculation", statistics_calculation)
    
    # Phase 4: Answer Generation
    workflow.add_node("generate_answer", generate_answer)
    
    # ===================
    # Define edges
    # ===================
    
    # Start -> Identify Attributes
    workflow.add_edge(START, "identify_attributes")
    
    # Conditional: Need building function lookup?
    workflow.add_conditional_edges(
        "identify_attributes",
        route_function_needed,
        {
            "needs_function": "embedding_search",
            "no_function": "generate_cypher_district"
        }
    )
    
    # Embedding search -> Generate Cypher
    workflow.add_edge("embedding_search", "generate_cypher_district")
    
    # Cypher generation -> Execute query
    workflow.add_edge("generate_cypher_district", "execute_query")
    
    # Conditional: Need spatial filtering?
    def route_spatial_filter_needed(state: AgentState) -> Literal["spatial_filter", "statistics"]:
        """Determine if spatial filtering is needed based on spatial_filter parameter."""
        has_spatial_filter = bool(state.get("spatial_filter"))
        
        if has_spatial_filter:
            # User provided spatial filter WKT - apply spatial filtering
            return "spatial_filter"
        else:
            # No spatial processing needed - go directly to statistics
            return "statistics"
    
    workflow.add_conditional_edges(
        "execute_query",
        route_spatial_filter_needed,
        {
            "spatial_filter": "spatial_filtering",
            "statistics": "statistics_calculation"
        }
    )
    
    # Spatial filtering -> Statistics
    workflow.add_edge("spatial_filtering", "statistics_calculation")
    
    # Statistics -> Answer
    workflow.add_edge("statistics_calculation", "generate_answer")
    
    # Answer -> End
    workflow.add_edge("generate_answer", END)
    
    return workflow


def compile_graph():
    """Compile the workflow into an executable graph."""
    workflow = create_workflow()
    return workflow.compile()


# Pre-compiled graph for import
graph = compile_graph()