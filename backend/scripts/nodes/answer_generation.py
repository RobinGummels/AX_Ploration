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
    # Limit either to general first 20 results. Sometimes all buildings are stored in results['buildings'], so limit to first 20 of those for context length
    results_to_show = results[:20]
    if "buildings" in results[0]:
        results_to_show = []
        for res in results:
            limited_res = res.copy()
            limited_res["buildings"] = res["buildings"][:20]
            results_to_show.append(limited_res)
            if len(results_to_show) >= 20:
                break
    results_text = json.dumps(results_to_show, ensure_ascii=False, indent=2)
    
    # Add building function context if used
    building_functions = state.get("building_functions", [])
    building_function_names = state.get("building_function_names", [])
    if building_functions and building_function_names and len(building_functions) == len(building_function_names):
        functions_text = ", ".join([f"{name} (Code: {code})" for code, name in zip(building_functions, building_function_names)])
        results_text = f"Gesuchte Gebäudefunktionen: {functions_text}\n\n" + results_text
    
    # Add spatial filtering information if applied
    spatial_filter = state.get("spatial_filter")
    if spatial_filter and spatial_comparison:
        mode = spatial_comparison.get("mode", "unknown")
        original_count = spatial_comparison.get("original_count", 0)
        filtered_count = spatial_comparison.get("filtered_count", 0)
        
        filter_description = ""
        if mode == "polygon_containment":
            filter_description = f"Räumliche Filterung: {original_count} Gebäude gefunden, {filtered_count} innerhalb der angegebenen Geometrie"
        elif mode == "nearest":
            count = spatial_comparison.get("count", 0)
            filter_description = f"Räumliche Filterung: Die {count} nächstgelegenen Gebäude von {original_count} gefundenen Gebäuden"
        elif mode == "radius":
            radius = spatial_comparison.get("radius_meters", 0)
            filter_description = f"Räumliche Filterung: {filtered_count} von {original_count} Gebäuden innerhalb von {radius}m Radius"
        
        if filter_description:
            results_text = f"{filter_description}\n\n" + results_text
    
    # Add spatial analysis if available (legacy)
    elif spatial_comparison:
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
