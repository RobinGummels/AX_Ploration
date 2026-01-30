"""
Generate schema template for LLM prompts from current Neo4j database.

Usage:
    python generate_schema_template.py [--output PATH]
    
This script queries the Neo4j database for its current structure and generates
a schema template file that can be imported by the prompts module.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.neo4j_client import neo4j_client


def get_node_labels() -> List[str]:
    """Get all node labels in the database."""
    query = "CALL db.labels() YIELD label RETURN label ORDER BY label"
    results = neo4j_client.execute_query(query)
    return [r['label'] for r in results]


def get_relationship_types() -> List[str]:
    """Get all relationship types in the database."""
    query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
    results = neo4j_client.execute_query(query)
    return [r['relationshipType'] for r in results]


def get_node_properties(label: str) -> Dict[str, str]:
    """Get properties and their types for a node label."""
    query = f"""
    MATCH (n:{label})
    WITH n LIMIT 100
    UNWIND keys(n) AS key
    WITH key, n[key] AS value
    RETURN DISTINCT key, valueType(value) AS type
    ORDER BY key
    """
    results = neo4j_client.execute_query(query)
    return {r['key']: r['type'] for r in results}


def get_node_count(label: str) -> int:
    """Get count of nodes for a label."""
    query = f"MATCH (n:{label}) RETURN count(n) AS count"
    result = neo4j_client.execute_query(query)
    return result[0]['count'] if result else 0


def get_relationship_info(rel_type: str) -> Dict[str, Any]:
    """Get information about a relationship type."""
    query = f"""
    MATCH (a)-[r:{rel_type}]->(b)
    RETURN DISTINCT labels(a)[0] AS source, labels(b)[0] AS target, count(r) AS count
    LIMIT 1
    """
    result = neo4j_client.execute_query(query)
    if result:
        r = result[0]
        return {
            'source': r['source'],
            'target': r['target'],
            'count': r['count']
        }
    return {}


def generate_schema_text() -> str:
    """Generate human-readable schema description for LLM prompts."""
    lines = []
    
    # Get all labels
    labels = get_node_labels()
    
    # Nodes section
    lines.append("Nodes:")
    for label in labels:
        properties = get_node_properties(label)
        count = get_node_count(label)
        
        # Format properties with types
        prop_str = ", ".join([f"{k} ({v})" for k, v in properties.items()])
        lines.append(f"- (:{label} {{{prop_str}}}) - {count:,} nodes")
    
    lines.append("")
    
    # Relationships section
    rel_types = get_relationship_types()
    if rel_types:
        lines.append("Relationships:")
        for rel_type in rel_types:
            info = get_relationship_info(rel_type)
            if info:
                lines.append(f"- ({info['source']})-[:{rel_type}]->({info['target']}) - {info.get('count', 0):,} instances")
    
    return "\n".join(lines)


def generate_schema_dict() -> Dict[str, Any]:
    """Generate structured schema as dictionary."""
    schema = {
        'nodes': {},
        'relationships': []
    }
    
    # Get node information
    labels = get_node_labels()
    for label in labels:
        schema['nodes'][label] = {
            'properties': get_node_properties(label),
            'count': get_node_count(label)
        }
    
    # Get relationship information
    rel_types = get_relationship_types()
    for rel_type in rel_types:
        info = get_relationship_info(rel_type)
        if info:
            schema['relationships'].append({
                'type': rel_type,
                'source': info['source'],
                'target': info['target'],
                'count': info.get('count', 0)
            })
    
    return schema


def generate_prompt_hints() -> List[str]:
    """Generate important hints for Cypher query generation."""
    hints = []
    
    # Get all labels
    labels = get_node_labels()
    
    # Check for integer vs string codes in Functions
    function_labels = [l for l in labels if 'function' in l.lower()]
    for label in function_labels:
        props = get_node_properties(label)
        if 'code' in props:
            code_type = props['code']
            # Extract just the base type (e.g., "INTEGER" from "INTEGER NOT NULL")
            base_type = code_type.split()[0] if ' ' in code_type else code_type
            if base_type == 'INTEGER':
                hints.append(f"WICHTIG: {label}.code ist INTEGER! Nutze [1010, 2020] NICHT ['1010', '2020']!")
            elif base_type == 'STRING':
                hints.append(f"ACHTUNG: {label}.code ist STRING! Nutze ['1010', '2020'] mit Quotes!")
    
    # Check for coordinate systems in Buildings
    building_labels = [l for l in labels if 'building' in l.lower()]
    for label in building_labels:
        props = get_node_properties(label)
        if 'centroid' in props:
            hints.append(f"{label}.centroid: Parse String und konvertiere zu Point für Distanzberechnungen. Achte darauf, dass der WKT-String ETRS89 Koordinaten nutzt!")
    
    # Check for coordinate systems in Districts
    district_labels = [l for l in labels if 'district' in l.lower() or 'gemeinde' in l.lower()]
    for label in district_labels:
        props = get_node_properties(label)
        if 'centroid' in props:
            hints.append(f"{label}.centroid: Achte darauf, dass der WKT-String WGS84 Koordinaten nutzt!")
    
    # Check for dual storage pattern (property + relationship)
    for label in building_labels:
        props = get_node_properties(label)
        # Check if properties exist that also have relationships
        if any(key in props for key in ['IN_DISTRICT', 'HAS_FUNCTION']):
            hints.append(f"{label} hat Properties UND Relationships - nutze Relationships für Joins!")
    
    # Check for nullable fields that might cause sorting issues
    for label in building_labels:
        props = get_node_properties(label)
        nullable_fields = [k for k, v in props.items() if 'NOT NULL' not in v]
        if nullable_fields:
            hints.append(f"Nullable Felder in {label}: Filtere NULL-Werte vor ORDER BY!")
    
    # General Hints:
    hints.append("WICHTIG: Function.code ist INTEGER! Nutze [1010, 2020] NICHT ['1010', '2020']!")
    hints.append("District.centroid: Achte darauf, dass der WKT-String WGS84 Koordinaten nutzt!")
    hints.append("Verwende immer MATCH statt OPTIONAL MATCH wenn möglich.")
    hints.append("Versuche immer deine Cyper-Queries so zu schreiben, dass du erst über MATCH die relevanten Knoten filterst, dann über WHERE weitere Bedingungen anwendest, und am Ende alle relevanten Gebäude mit collect(b) AS buildings zurückgibst.")
    return hints


def save_schema_template(output_path: str = None):
    """Generate and save schema template to Python file."""
    if output_path is None:
        # Default: save to scripts/utils/schema_template.py
        script_dir = Path(__file__).parent.parent / 'scripts' / 'utils'
        output_path = script_dir / 'schema_template.py'
    else:
        output_path = Path(output_path)
    
    print("Querying Neo4j database for schema information...")
    
    # Generate schema components
    schema_text = generate_schema_text()
    schema_dict = generate_schema_dict()
    hints = generate_prompt_hints()
    
    print("\nFound:")
    print(f"  - {len(schema_dict['nodes'])} node labels")
    print(f"  - {len(schema_dict['relationships'])} relationship types")
    print(f"  - {len(hints)} important hints")
    
    # Generate Python file content
    content = f'''"""
Auto-generated schema template from Neo4j database.

Generated by: backend/db/generate_schema_template.py
Last updated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DO NOT EDIT THIS FILE MANUALLY!
Run `python backend/db/generate_schema_template.py` to regenerate.
"""

import json

# Human-readable schema description for LLM prompts
SCHEMA_TEXT = """\\
{schema_text}
"""

# Structured schema as dictionary
SCHEMA_DICT = {json.dumps(schema_dict, indent=4, ensure_ascii=False)}

# Important hints for Cypher query generation
SCHEMA_HINTS = {json.dumps(hints, indent=4, ensure_ascii=False)}


def get_schema_for_prompt() -> str:
    """
    Get formatted schema text for inclusion in LLM prompts.
    
    Returns:
        Formatted schema description with nodes, relationships, and hints.
    """
    parts = [SCHEMA_TEXT]
    
    if SCHEMA_HINTS:
        parts.append("\\nWichtige Hinweise:")
        for hint in SCHEMA_HINTS:
            parts.append(f"- {{hint}}")
    
    return "\\n".join(parts)


def get_schema_dict() -> dict:
    """
    Get structured schema as dictionary.
    
    Returns:
        Dictionary with 'nodes' and 'relationships' keys.
    """
    return SCHEMA_DICT
'''
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ Schema template saved to: {output_path}")
    print("\nYou can now import it in prompts.py:")
    print("  from .schema_template import get_schema_for_prompt")
    
    return output_path


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate schema template from Neo4j database"
    )
    parser.add_argument(
        '--output', '-o',
        help='Output path for schema template (default: scripts/utils/schema_template.py)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Verify Neo4j connection
    if not neo4j_client.verify_connection():
        print("ERROR: Could not connect to Neo4j database!")
        print("Check your NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in .env file.")
        sys.exit(1)
    
    try:
        save_schema_template(args.output)
        print("\n✓ Schema template generation complete!")
        
    except Exception as e:
        print(f"\n✗ Error generating schema template: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
