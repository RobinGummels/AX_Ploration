"""Node for generating the final user-facing answer."""

from typing import Dict, Any
import json

from ..models import AgentState
from ..utils.llm_client import llm_client
from ..utils.prompts import PROMPTS


def generate_answer(state: AgentState) -> Dict[str, Any]:
    """
    Node: Generate a human-readable answer from query results.
    
    Takes the raw results and any spatial analysis, and creates
    a formatted, user-friendly response in German.
    
    Args:
        state: Current agent state with 'results' and optionally 'spatial_comparison'
        
    Returns:
        Dict with 'final_answer' for the user
    """
    query = state["query"]
    results = state.get("results", [])
    spatial_comparison = state.get("spatial_comparison")
    error = state.get("error")
    
    # Handle error cases
    if error:
        return {
            "final_answer": f"Es ist ein Fehler aufgetreten: {error}",
            "messages": ["Generated error response"]
        }
    
    # Handle empty results
    if not results:
        return {
            "final_answer": "Leider wurden keine Ergebnisse für Ihre Anfrage gefunden. "
                           "Bitte versuchen Sie es mit einer anderen Suchanfrage.",
            "messages": ["No results found, generated empty response"]
        }
    
    # Format results for the LLM
    # Limit to first 20 results for context length
    results_to_show = results[:20]
    results_text = json.dumps(results_to_show, ensure_ascii=False, indent=2)
    
    # Add spatial analysis if available
    if spatial_comparison:
        results_text += f"\n\nRäumliche Analyse:\n{json.dumps(spatial_comparison, ensure_ascii=False, indent=2)}"
    
    # Add note if results were truncated
    if len(results) > 20:
        results_text += f"\n\n(Zeige 20 von {len(results)} Ergebnissen)"
    
    prompt = PROMPTS["generate_answer"]
    
    messages = [
        {"role": "system", "content": prompt["system"]},
        {"role": "user", "content": prompt["user"].format(
            query=query,
            results=results_text
        )}
    ]
    
    try:
        answer = llm_client.chat_completion(messages)
        
        return {
            "final_answer": answer,
            "messages": [f"Generated answer for {len(results)} results"]
        }
        
    except Exception as e:
        # Fallback: Generate a basic answer without LLM
        basic_answer = f"Ihre Anfrage ergab {len(results)} Ergebnisse."
        
        if spatial_comparison and spatial_comparison.get("statistics"):
            stats = spatial_comparison["statistics"]
            if "floors_above" in stats:
                basic_answer += f"\nDurchschnittliche Stockwerke: {stats['floors_above']['avg']:.1f}"
        
        return {
            "final_answer": basic_answer,
            "error": f"Error in answer generation, using fallback: {str(e)}",
            "messages": [f"Error in answer generation: {str(e)}"]
        }
