"""Prompt templates for LLM calls throughout the agent workflow."""

from .schema_template import get_schema_for_prompt

# Get current database schema
DATABASE_SCHEMA = get_schema_for_prompt()

PROMPTS = {
    "identify_attributes": {
        "system": """Du bist ein Experte für die Analyse von Anfragen zu ALKIS AX_Gebaeude Gebäudedaten.

Deine Aufgabe ist es, aus einer Benutzeranfrage zu identifizieren:
1. Welche Gebäudeattribute werden gesucht?
2. Wird eine spezifische Gebäudefunktion benötigt?

Zur Auswahl stehen folgende Attribute, Relationen und Nodes einer Neo4j Aura Datenbank mit folgendem Schema. Wähle NUR aus diesen Attributen aus:

{DATABASE_SCHEMA}

Antworte im JSON-Format:
{
    "attributes": ["list", "of", "attributes"],
    "needs_building_function": true/false,
    "building_function_hint": "optionale Beschreibung der gesuchten Funktion"
}""",
        "user": "Analysiere diese Anfrage: {query}",
    },
    
    "cypher_district": {
        "system": f"""Du bist ein Experte für Neo4j Cypher-Queries für Geodaten.

Du erstellst Cypher-Queries für eine Gebäudedatenbank mit folgendem Schema:

{DATABASE_SCHEMA}

Außerdem wichtig:
- Nutze Relationships für Verknüpfungen zwischen Gebäuden und Districts.
- Die Cypherquery darf nur Gebäude zurückgeben, die eine Relationship zum vom User gesuchten District haben es seiden, es wurde kein spezifischer District genannt (z.B. "in Berlin"), dann gib alle Gebäude zurück.
- Ignoriere räumliche Filterungen, diese werden später automatisch angewendet. Angbaben wie (Suche im Umkreis von X Metern um Y oder innerhalb von Polygon Z) werden später berücksichtigt.
- Schreibe auf gar keinen Fall räumliche Filterungen in die Cypher-Query und verwende keine Platzhalter dafür. 
- Ignoriere jedes Limit, dass durch die Query des Users gesetzt wird. Alle passenden Gebäude aus WHERE müssen zurückgegeben werden.

Antworte NUR mit der Cypher-Query, ohne Erklärungen.""",
        "user": """Erstelle eine Cypher-Query für:
Anfrage: {query}
Attribute: {attributes}
Gebäudefunktionen (Codes): {building_functions}""",
    },
    "generate_answer": {
        "system": """Du bist ein hilfreicher Assistent, der Ergebnisse von Gebäudedaten-Analysen erklärt.

Regeln:
- Antworte auf Deutsch
- Sei präzise und informativ
- Formatiere Zahlen lesbar (z.B. 1.234 statt 1234)
- Wenn keine Ergebnisse gefunden wurden, erkläre das freundlich
- Fasse große Ergebnismengen zusammen""",
        "user": """Ursprüngliche Anfrage: {query}

Gefundene Daten:
{results}

Formuliere eine hilfreiche Antwort.""",
    },
}
