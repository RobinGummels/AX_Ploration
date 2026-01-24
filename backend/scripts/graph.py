from langgraph.graph import StateGraph, START, END
from typing import Literal

from .models import AgentState
from .nodes import (
    identify_attributes,
    embedding_search,
    interpret_query,
    generate_cypher_district,
    generate_cypher_stats,
    execute_query,
    spatial_filtering,
    generate_answer,
    route_function_needed,
    route_query_type
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
    workflow.add_node("interpret_query", interpret_query)
    
    # Phase 2: Cypher Generation (different strategies)
    workflow.add_node("generate_cypher_district", generate_cypher_district)
    workflow.add_node("generate_cypher_stats", generate_cypher_stats)
    
    # Phase 3: Data Retrieval & Processing
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("spatial_filtering", spatial_filtering)
    
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
            "no_function": "interpret_query"
        }
    )
    
    # Embedding search -> Interpret query
    workflow.add_edge("embedding_search", "interpret_query")
    
    # Conditional: Which query type?
    workflow.add_conditional_edges(
        "interpret_query",
        route_query_type,
        {
            "district": "generate_cypher_district",
            "statistics": "generate_cypher_stats"
        }
    )
    
    # All cypher generators -> Execute query
    workflow.add_edge("generate_cypher_district", "execute_query")
    workflow.add_edge("generate_cypher_stats", "execute_query")
    
    # Conditional: Need spatial filtering?
    def route_spatial_filter_needed(state: AgentState) -> Literal["spatial_filter", "answer"]:
        """Determine if spatial filtering is needed based on spatial_filter parameter."""
        has_spatial_filter = bool(state.get("spatial_filter"))
        
        if has_spatial_filter:
            # User provided spatial filter WKT - apply spatial filtering
            return "spatial_filter"
        else:
            # No spatial processing needed
            return "answer"
    
    workflow.add_conditional_edges(
        "execute_query",
        route_spatial_filter_needed,
        {
            "spatial_filter": "spatial_filtering",
            "answer": "generate_answer"
        }
    )
    
    # Spatial filtering -> Answer
    workflow.add_edge("spatial_filtering", "generate_answer")
    
    # Answer -> End
    workflow.add_edge("generate_answer", END)
    
    return workflow


def compile_graph():
    """Compile the workflow into an executable graph."""
    workflow = create_workflow()
    return workflow.compile()


# Pre-compiled graph for import
graph = compile_graph()