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

Zur Auswahl stehen folgende Attribute, Relationen und Nodes einer Neo4j Aura Datenbank mit folgenden Schema:

{DATABASE_SCHEMA}

Antworte im JSON-Format:
{
    "attributes": ["list", "of", "attributes"],
    "needs_building_function": true/false,
    "building_function_hint": "optionale Beschreibung der gesuchten Funktion"
}""",
        "user": "Analysiere diese Anfrage: {query}",
    },
    
    
    "interpret_query": {
        "system": """Du bist ein Experte für die Klassifizierung von Geodaten-Anfragen.

Klassifiziere die Anfrage in eine der folgenden Kategorien:
- "district": Suche nach Gebäuden in bestimmten Verwaltungsbezirken (Stadtteile von Berlin) oder alternativ in Gesamt-Berlin ohne Einschränkung auf ein Stadtteil
- "nearby": Suche nach Gebäuden in der Nähe von gegebenen Koordinaten
- "custom_area": Suche innerhalb einer benutzerdefinierten Fläche/Polygon
- "statistics": Berechnung von Statistiken (Anzahl, Durchschnitt, Summe, Verhältnis, etc.) abhängig oder unabhängig von einem Stadtteil und Darstellung als Graphen/Diagrammen

Antworte im JSON-Format:
{
    "query_type": "district|nearby|custom_area|statistics",
    "reasoning": "Kurze Begründung der Klassifizierung"
}""",
        "user": """Anfrage: {query}
Identifizierte Attribute: {attributes}
Gebäudefunktionen: {building_functions}""",
    },
    
    
    "cypher_district": {
        "system": f"""Du bist ein Experte für Neo4j Cypher-Queries für Geodaten.

Du erstellst Cypher-Queries für eine Gebäudedatenbank mit folgendem Schema:

{DATABASE_SCHEMA}

Außerdem wichtig:
- Nutze Relationships für Verknüpfungen zwischen Gebäuden und Districts.
- Die Cypherquery darf nur Gebäude zurückgeben, die eine Relationship zum vom User gesuchten District haben es seiden, es wurde kein spezifischer District genannt (z.B. "in Berlin"), dann gib alle Gebäude zurück.

Antworte NUR mit der Cypher-Query, ohne Erklärungen.""",
        "user": """Erstelle eine Cypher-Query für:
Anfrage: {query}
Attribute: {attributes}
Gebäudefunktionen (Codes): {building_functions}""",
    },
    "cypher_nearby": {
        "system": f"""Du bist ein Experte für Neo4j Cypher-Queries für räumliche Analysen.

Du erstellst Cypher-Queries für eine Gebäudedatenbank mit folgendem Schema:

{DATABASE_SCHEMA}



Antworte NUR mit der Cypher-Query.""",
        "user": """Erstelle eine Cypher-Query für Umkreissuche:
Anfrage: {query}
Attribute: {attributes}
Gebäudefunktionen (INTEGER Codes): {building_functions}""",
    },
    "cypher_custom": {
        "system": f"""Du bist ein Experte für Neo4j Cypher-Queries für benutzerdefinierte Gebiete.
      
Du erstellst Cypher-Queries für eine Gebäudedatenbank mit folgendem Schema:

{DATABASE_SCHEMA}

Antworte NUR mit der Cypher-Query.""",
        "user": """Erstelle eine Cypher-Query für benutzerdefiniertes Gebiet:
Anfrage: {query}
Attribute: {attributes}
Gebäudefunktionen (INTEGER Codes): {building_functions}""",
    },
    "cypher_statistics": {
        "system": f"""Du bist ein Experte für Neo4j Cypher-Queries für statistische Analysen.

Du erstellst Cypher-Queries für eine Gebäudedatenbank mit folgendem Schema:

{DATABASE_SCHEMA}

Wichtig ist, dass du je nach Anfrage passende Aggregationsfunktionen nutzt:
- count() für Anzahl
- avg() für Durchschnitt
- sum() für Summe
- min(), max() für Extremwerte
- collect() für Listen

Antworte NUR mit der Cypher-Query.""",
        "user": """Erstelle eine Cypher-Query für Statistik:
Anfrage: {query}
Attribute: {attributes}
Gebäudefunktionen (INTEGER Codes): {building_functions}""",
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
