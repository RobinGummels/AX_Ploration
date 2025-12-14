from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    query: str                          # User query
    attributes: List[str]               # Identified building attributes
    building_functions: List[str]       # Found building functions
    query_type: str                     # "district" | "nearby" | "custom_area" | "statistics"
    cypher_query: str                   # Generated Cypher query
    results: List[Dict]                 # Data from Neo4j
    spatial_comparison: Optional[Dict]  # Spatial comparison results
    final_answer: str                   # Final answer