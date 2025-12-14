"""
AX_Ploration Agent - Main Entry Point

Usage:
    python -m scripts.main "Finde alle Wohngebäude in Münster"
    
Or as a module:
    from scripts.main import run_agent
    result = run_agent("Finde alle Wohngebäude in Münster")
"""

import sys
from typing import Dict, Any

from .config import validate_config
from .graph import graph
from .models import AgentState
from .utils.neo4j_client import neo4j_client


def create_initial_state(query: str) -> AgentState:
    """Create the initial state for a new agent run."""
    return {
        "query": query,
        "attributes": [],
        "needs_building_function": False,
        "building_functions": [],
        "building_function_descriptions": [],
        "query_type": "",
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
        final_state = graph.invoke(initial_state)
        
        if verbose:
            print("\nProcessing steps:")
            for msg in final_state.get("messages", []):
                print(f"  - {msg}")
            print("-" * 50)
            print(f"\nFinal answer: {final_state.get('final_answer', 'No answer generated')}")
        
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