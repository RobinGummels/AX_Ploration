from typing import TypedDict, List, Dict, Optional, Any, Annotated
from operator import add

class AgentState(TypedDict):
    """Central state object passed through the LangGraph workflow."""
    
    # Input
    query: str                                      # Original user query
    spatial_filter: Optional[str]                   # Optional WKT geometry for spatial filtering (EPSG:25833)
    query_language: Optional[str]                   # Detected query language (e.g., "de", "en")
    
    # Attribute Identification
    attributes: List[str]                           # Identified building attributes (e.g., "floors", "function", "area")
    needs_building_function: bool                   # Whether building function lookup is needed
    building_function_query: Optional[str]          # Extracted building function-relevant query for embedding search
    
    # Building Function Search
    building_functions: List[int]                   # Found building function codes (e.g., 1010, 2000)
    building_function_names: List[str]              # Function names (e.g., "Wohnhaus", "Wohngebäude")
    building_function_descriptions: List[str]       # Full descriptions
    
    # Cypher Generation (always district query type)
    cypher_query: str                               # Generated Cypher query
    
    # Data Retrieval & Statistics
    results: List[Dict[str, Any]]                   # Results with structure: [{"buildings": [...], "statistics": {...}}]
    
    # Spatial Processing (optional)
    spatial_comparison: Optional[Dict[str, Any]]    # Results from spatial filtering metadata
    
    # Output
    final_answer: str                               # Final formatted answer for user
    
    # Error handling
    error: Optional[str]                            # Error message if something went wrong
    
    # Metadata
    messages: Annotated[List[str], add]             # Log of processing steps


class BuildingFunction(TypedDict):
    """Represents a building function from the database."""
    code: int
    name: str
    description: str
    embedding_small: Optional[List[float]]
    embedding_large: Optional[List[float]]