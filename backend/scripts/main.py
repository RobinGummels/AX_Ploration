"""
AX_Ploration Agent - Main Entry Point

Usage:
    python -m scripts.main "Finde alle Wohngebäude in Münster"
    
Or as a module:
    from scripts.main import run_agent
    result = run_agent("Finde alle Wohngebäude in Münster")
"""

import sys
import json
from typing import Dict, Any

from .config import validate_config
from .graph import graph
from .models import AgentState
from .utils.neo4j_client import neo4j_client


def print_state_update(state: AgentState, step_name: str = ""):
    """Print detailed state information for debugging."""
    print(f"\n{'='*60}")
    if step_name:
        print(f"STEP: {step_name}")
    print(f"{'='*60}")
    
    # Attributes
    attributes = state.get('attributes', [])
    if attributes:
        print(f"Attributes: {attributes}")
    
    # Building Functions
    building_functions = state.get('building_functions', [])
    building_function_names = state.get('building_function_names', [])
    if building_functions:
        if building_function_names and len(building_functions) == len(building_function_names):
            functions_display = [f"{code} ({name})" for code, name in zip(building_functions, building_function_names)]
            print(f"Building Functions: {', '.join(functions_display)}")
        else:
            print(f"Building Functions: {building_functions}")
    
    # Query Type
    query_type = state.get('query_type', '')
    if query_type:
        print(f"Query Type: {query_type}")
    
    # Cypher Query
    cypher = state.get('cypher_query', '')
    if cypher:
        print("Generated Cypher Query:")
        print("-" * 60)
        print(cypher)
        print("-" * 60)
    
    # Results
    results = state.get('results', [])
    if results:
        print(f"Results: {len(results)} items found")
        # Show first 3 results as sample
        if len(results) > 0:
            print("Sample results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {json.dumps(result, ensure_ascii=False, default=str)[:100]}...")
    
    # Spatial Comparison
    spatial = state.get('spatial_comparison')
    if spatial:
        print("Spatial Comparison:")
        print(f"  {json.dumps(spatial, ensure_ascii=False, indent=2, default=str)[:200]}...")
    
    # Error
    error = state.get('error')
    if error:
        print(f"ERROR: {error}")
    
    # Messages
    messages = state.get('messages', [])
    if messages:
        print("Messages:")
        for msg in messages:
            print(f"  • {msg}")
    
    print(f"{'='*60}\n")


def create_initial_state(query: str, spatial_filter: str = None) -> AgentState:
    """Create the initial state for a new agent run.
    
    Args:
        query: The user's natural language query
        spatial_filter: Optional WKT geometry string in EPSG:25833 for spatial filtering
    """
    return {
        "query": query,
        "spatial_filter": spatial_filter,
        "attributes": [],
        "needs_building_function": False,
        "building_functions": [],
        "building_function_names": [],
        "building_function_descriptions": [],
        "cypher_query": "",
        "results": [],
        "spatial_comparison": None,
        "final_answer": "",
        "error": None,
        "messages": []
    }


def run_agent(query: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Run the AX_Ploration agent with a user query.
    
    Args:
        query: The user's natural language query
        verbose: If True, print intermediate steps
        
    Returns:
        Dict containing the final state with 'final_answer' and other results
    """
    # Validate configuration
    validate_config()
    
    # Verify Neo4j connection
    if not neo4j_client.verify_connection():
        return {
            "error": "Could not connect to Neo4j database",
            "final_answer": "Entschuldigung, ich konnte keine Verbindung zur Datenbank herstellen."
        }
    
    # Create initial state
    initial_state = create_initial_state(query)
    
    if verbose:
        print(f"Processing query: {query}")
        print("-" * 50)
    
    # Run the graph
    try:
        if verbose:
            
            # Print query
            print("\n" + "="*60)
            print("INITIAL STATE")
            print("="*60)
            print(f"Query: {initial_state.get('query', 'N/A')}")
            print("="*60)
            
            # Stream the graph execution to see intermediate steps
            print("\n" + "="*60)
            print("EXECUTING AGENT WORKFLOW")
            print("="*60)
            
            final_state = None
            for step_output in graph.stream(initial_state):
                # Each step_output is a dict with node_name: updated_state
                for node_name, updated_state in step_output.items():
                    print_state_update(updated_state, f"After Node: {node_name}")
                    final_state = updated_state
            
            if final_state:
                print("\n" + "="*60)
                print("FINAL ANSWER")
                print("="*60)
                print(final_state.get('final_answer', 'No answer generated'))
                print("="*60 + "\n")
        else:
            final_state = graph.invoke(initial_state)
        
        return final_state
        
    except Exception as e:
        error_msg = f"Error during agent execution: {str(e)}"
        if verbose:
            print(f"ERROR: {error_msg}")
        return {
            "error": error_msg,
            "final_answer": "Entschuldigung, bei der Verarbeitung ist ein Fehler aufgetreten."
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AX_Ploration Agent")
    parser.add_argument("query", help="Natural language query about buildings, their functions and attributes in Berlin")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print processing steps")
    
    args = parser.parse_args()
    
    result = run_agent(args.query, verbose=args.verbose)
    
    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()