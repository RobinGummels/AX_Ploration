from langgraph.graph import StateGraph, START, END
from typing import Literal

from .models import AgentState
from .nodes import (
    identify_attributes,
    embedding_search,
    interpret_query,
    generate_cypher_district,
    generate_cypher_nearby,
    generate_cypher_custom,
    generate_cypher_stats,
    execute_query,
    spatial_comparison,
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
    workflow.add_node("generate_cypher_nearby", generate_cypher_nearby)
    workflow.add_node("generate_cypher_custom", generate_cypher_custom)
    workflow.add_node("generate_cypher_stats", generate_cypher_stats)
    
    # Phase 3: Data Retrieval & Processing
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("spatial_comparison", spatial_comparison)
    
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
            "nearby": "generate_cypher_nearby",
            "custom_area": "generate_cypher_custom",
            "statistics": "generate_cypher_stats"
        }
    )
    
    # All cypher generators -> Execute query
    workflow.add_edge("generate_cypher_district", "execute_query")
    workflow.add_edge("generate_cypher_nearby", "execute_query")
    workflow.add_edge("generate_cypher_custom", "execute_query")
    workflow.add_edge("generate_cypher_stats", "execute_query")
    
    # Conditional: Need spatial comparison?
    def route_spatial_needed(state: AgentState) -> Literal["spatial", "answer"]:
        """Determine if spatial comparison is needed."""
        query_type = state.get("query_type", "")
        if query_type in ["nearby", "custom_area"]:
            return "spatial"
        return "answer"
    
    workflow.add_conditional_edges(
        "execute_query",
        route_spatial_needed,
        {
            "spatial": "spatial_comparison",
            "answer": "generate_answer"
        }
    )
    
    # Spatial comparison -> Answer
    workflow.add_edge("spatial_comparison", "generate_answer")
    
    # Answer -> End
    workflow.add_edge("generate_answer", END)
    
    return workflow


def compile_graph():
    """Compile the workflow into an executable graph."""
    workflow = create_workflow()
    return workflow.compile()


# Pre-compiled graph for import
graph = compile_graph()