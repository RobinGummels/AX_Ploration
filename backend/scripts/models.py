from typing import TypedDict, List, Dict, Optional, Any, Annotated
from operator import add

class AgentState(TypedDict):
    """Central state object passed through the LangGraph workflow."""
    
    # Input
    query: str                                      # Original user query
    
    # Attribute Identification
    attributes: List[str]                           # Identified building attributes (e.g., "floors", "function", "area")
    needs_building_function: bool                   # Whether building function lookup is needed
    
    # Building Function Search
    building_functions: List[str]                   # Found building function codes (e.g., "1010", "2000")
    building_function_descriptions: List[str]       # Human-readable descriptions
    
    # Query Interpretation
    query_type: str                                 # "district" | "nearby" | "custom_area" | "statistics"
    
    # Cypher Generation
    cypher_query: str                               # Generated Cypher query
    
    # Data Retrieval
    results: List[Dict[str, Any]]                   # Raw data from Neo4j
    
    # Spatial Processing (optional)
    spatial_comparison: Optional[Dict[str, Any]]    # Results from spatial comparison
    
    # Output
    final_answer: str                               # Final formatted answer for user
    
    # Error handling
    error: Optional[str]                            # Error message if something went wrong
    
    # Metadata
    messages: Annotated[List[str], add]             # Log of processing steps


class BuildingFunction(TypedDict):
    """Represents a building function from the database."""
    code: str
    description: str
    parent_code: Optional[str]
    embedding: Optional[List[float]]