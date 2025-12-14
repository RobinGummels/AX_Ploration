from langgraph.graph import StateGraph, START
from typing import TypedDict

# Import your custom functions
from your_module import (
    identify_attributes,
    check_building_function_needed,
    embedding_search,
    interpret_query,
    generate_cypher_district,
    route_function_needed,
    route_query_type
)

# Define your AgentState
class AgentState(TypedDict):
    # Add your state fields here
    pass

workflow = StateGraph(AgentState)

# Nodes hinzufügen
workflow.add_node("identify_attributes", identify_attributes)
workflow.add_node("check_function", check_building_function_needed)
workflow.add_node("embedding_search", embedding_search)
workflow.add_node("interpret_query", interpret_query)
workflow.add_node("generate_cypher_district", generate_cypher_district)
# ... weitere nodes

# Edges definieren
workflow.add_edge(START, "identify_attributes")

# Conditional branching
workflow.add_conditional_edges(
    "identify_attributes",
    route_function_needed,  # Funktion die entscheidet
    {
        "needs_function": "embedding_search",
        "no_function": "interpret_query"
    }
)

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

# ... weitere conditional edges und normale edges