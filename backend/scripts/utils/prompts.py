"""Prompt templates for LLM calls throughout the agent workflow."""

from .schema_template import get_schema_for_prompt

# Get current database schema
DATABASE_SCHEMA = get_schema_for_prompt()

PROMPTS = {
    "identify_attributes": {
        "system": f"""You are an expert in analyzing queries about ALKIS AX_Gebaeude building data.

Your task is to identify from a user query:
1. Which building attributes are being searched for?
2. Is a specific building function needed?
3. Extract ONLY the building function-relevant parts (remove location, statistics, filters)
4. Detect the query language (full language name, e.g., "German", "English", "French", etc.)

Available attributes from Neo4j Aura database schema - choose ONLY from these:

{DATABASE_SCHEMA}

Respond in JSON format:
{{
    "attributes": ["list", "of", "attributes"],
    "needs_building_function": true/false,
    "building_function_query": "extracted terms regarding the building function (e.g., 'schools', 'Wohngebäude', 'hospitals')",
    "query_language": "Full language name (e.g., 'German', 'English', 'French', etc.)"
}}

Examples:
- Query: "Wie viele Schulen gibt es in Pankow?" -> building_function_query: "Schulen", query_language: "German"
- Query: "Show me hospitals with more than 3 floors" -> building_function_query: "hospitals", query_language: "English"
- Query: "Liste alle Gebäude auf in denen Vertretungen ausländische Regierungen sitzen" -> building_function_query: "Gebäude mit Vertretungen ausländischer Regierungen", query_language: "German"
""",
        "user": "Analyze this query: {query}",
    },
    
    "cypher_district": {
        "system": f"""Du bist ein Experte für Neo4j Cypher-Queries für Geodaten.

Du erstellst Cypher-Queries für eine Gebäudedatenbank mit folgendem Schema:

{DATABASE_SCHEMA}

Außerdem wichtig:
- Nutze Relationships für Verknüpfungen zwischen Gebäuden und Districts.
- Die Cypherquery darf nur Gebäude zurückgeben, die eine Relationship zum vom User gesuchten District haben es seiden, es wurde kein spezifischer District genannt (z.B. "in Berlin"), dann gib alle Gebäude zurück.
- Die einzigen Districts, nach dem die Suche eingeschränkt werden darf sind "Mitte", "Friedrichshain-Kreuzberg", "Pankow". Wenn ein anderer District im User-Query genannt wird, ignoriere diesen.
- Ignoriere räumliche Filterungen, diese werden später automatisch angewendet. Angbaben wie (Suche im Umkreis von X Metern um Y oder innerhalb von Polygon Z) werden später berücksichtigt.
- Schreibe auf gar keinen Fall räumliche Filterungen in die Cypher-Query und verwende keine Platzhalter dafür. 
- Ignoriere jedes Limit, dass durch die Query des Users gesetzt wird. Alle passenden Gebäude aus WHERE müssen zurückgegeben werden.
- Verwende immer explizit collect(b) AS buildings. Schränke die Attribute der Buildings nicht weiter ein indem du collect({{name: b.name, id: b.id}}) AS buildings oder ähnliches nutzt. Gebe immer alle Attribute zurück.

Antworte NUR mit der Cypher-Query, ohne Erklärungen.""",
        "user": """Erstelle eine Cypher-Query für:
Anfrage: {query}
Attribute: {attributes}
Gebäudefunktionen (Codes): {building_functions}""",
    },
    "generate_answer": {
        "system": """You are a helpful assistant explaining building data analysis results.

IMPORTANT: Respond in {language} as the user's query was in {language}.

Rules:
- Be precise and informative
- Format numbers readable (e.g., 1,234 instead of 1234)
- If no results found, explain it friendly
- Summarize large result sets
- Maintain the query language in your response""",
        "user": """Original query: {query}

Found data:
{results}

Formuliere eine hilfreiche Antwort.""",
    },    "spatial_filter_mode": {
        "system": """You are an expert in analyzing spatial query intents.

Analyze the user query to determine which type of spatial filtering is desired:
1. **Nearest X buildings** to a point
2. All buildings **within radius X** from a point

Respond in JSON format:
{{
    "mode": "nearest" or "radius",
    "value": <number>,
    "reasoning": "Brief explanation"
}}

Examples:
- "Show me the 5 nearest schools" → {{"mode": "nearest", "value": 5}}
- "Find all buildings within 500m" → {{"mode": "radius", "value": 500}}
- "Which hospitals are nearby?" → {{"mode": "nearest", "value": 10}} (default: 10)
- "Buildings within 1km" → {{"mode": "radius", "value": 1000}}

Default values if not specified:
- For "nearest": value=10
- For "radius": value=500 (in meters)

If unclear whether "nearest" or "radius" is meant, choose "nearest" as default.

Respond ONLY with the JSON object, no additional explanations.""",
        "user": """User query: \"{query}\"
Spatial filter: Point geometry (WKT: {spatial_filter_wkt})

Determine the spatial filtering mode.""",
    },}
