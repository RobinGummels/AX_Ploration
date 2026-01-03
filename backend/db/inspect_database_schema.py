#!/usr/bin/env python3
"""Comprehensive database schema inspection for Neo4j.

This script provides detailed information about:
- All node labels with counts
- All properties per label with types and examples
- All relationships with types and counts
- Sample queries for each node type
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import json


def load_config():
    """Load Neo4j configuration from environment."""
    load_dotenv()
    return {
        "uri": os.getenv("NEO4J_URI"),
        "user": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD"),
        "database": os.getenv("NEO4J_DATABASE", "neo4j"),
    }


def get_all_labels(session):
    """Get all node labels with counts."""
    result = session.run("""
        MATCH (n)
        UNWIND labels(n) AS label
        RETURN label, count(*) AS count
        ORDER BY count DESC
    """)
    return [dict(record) for record in result]


def get_properties_for_label(session, label):
    """Get all properties and their types for a given label."""
    result = session.run(f"""
        MATCH (n:{label})
        WITH n LIMIT 100
        UNWIND keys(n) AS key
        WITH key, n[key] AS value
        RETURN DISTINCT key, 
               valueType(value) AS type,
               count(*) AS occurrences
        ORDER BY occurrences DESC
    """)
    return [dict(record) for record in result]


def get_sample_nodes(session, label, limit=3):
    """Get sample nodes for a label."""
    result = session.run(f"""
        MATCH (n:{label})
        RETURN n
        LIMIT {limit}
    """)
    samples = []
    for record in result:
        node = record["n"]
        samples.append({
            "labels": list(node.labels),
            "properties": dict(node)
        })
    return samples


def get_all_relationships(session):
    """Get all relationship types with counts."""
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) AS relationship_type, count(*) AS count
        ORDER BY count DESC
    """)
    return [dict(record) for record in result]


def get_relationship_details(session, rel_type):
    """Get details about a specific relationship type."""
    result = session.run(f"""
        MATCH (a)-[r:{rel_type}]->(b)
        WITH labels(a)[0] AS from_label, 
             labels(b)[0] AS to_label, 
             count(*) AS count
        RETURN from_label, to_label, count
        ORDER BY count DESC
        LIMIT 10
    """)
    return [dict(record) for record in result]


def get_indexes(session):
    """Get all indexes in the database."""
    result = session.run("SHOW INDEXES")
    return [dict(record) for record in result]


def get_constraints(session):
    """Get all constraints in the database."""
    result = session.run("SHOW CONSTRAINTS")
    return [dict(record) for record in result]


def main():
    config = load_config()
    driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
    
    print("=" * 80)
    print("NEO4J DATABASE SCHEMA INSPECTION")
    print("=" * 80)
    print()
    
    with driver.session(database=config["database"]) as session:
        # 1. Get all labels
        print("1. NODE LABELS")
        print("-" * 80)
        labels = get_all_labels(session)
        for label_info in labels:
            print(f"  {label_info['label']}: {label_info['count']:,} nodes")
        print()
        
        # 2. Detailed property analysis for each label
        print("2. PROPERTIES PER LABEL")
        print("-" * 80)
        for label_info in labels:
            label = label_info['label']
            print(f"\n  Label: {label} ({label_info['count']:,} nodes)")
            print(f"  {'-' * 70}")
            
            properties = get_properties_for_label(session, label)
            for prop in properties:
                print(f"    • {prop['key']}: {prop['type']} (in {prop['occurrences']} nodes)")
            
            # Get sample nodes
            samples = get_sample_nodes(session, label, limit=2)
            if samples:
                print(f"\n    Sample nodes:")
                for i, sample in enumerate(samples, 1):
                    print(f"\n    Sample {i}:")
                    for key, value in sample['properties'].items():
                        # Truncate long values
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        print(f"      {key}: {value_str}")
        
        print("\n")
        
        # 3. Relationships
        print("3. RELATIONSHIPS")
        print("-" * 80)
        relationships = get_all_relationships(session)
        
        if relationships:
            for rel in relationships:
                print(f"\n  Relationship: {rel['relationship_type']} ({rel['count']:,} instances)")
                details = get_relationship_details(session, rel['relationship_type'])
                for detail in details:
                    print(f"    ({detail['from_label']})-[:{rel['relationship_type']}]->({detail['to_label']}): {detail['count']:,}")
        else:
            print("  No relationships found in database")
        
        print("\n")
        
        # 4. Indexes
        print("4. INDEXES")
        print("-" * 80)
        try:
            indexes = get_indexes(session)
            if indexes:
                for idx in indexes:
                    print(f"  • {idx.get('name', 'N/A')}: {idx.get('type', 'N/A')} on {idx.get('labelsOrTypes', 'N/A')}")
            else:
                print("  No indexes found")
        except Exception as e:
            print(f"  Could not retrieve indexes: {e}")
        
        print("\n")
        
        # 5. Constraints
        print("5. CONSTRAINTS")
        print("-" * 80)
        try:
            constraints = get_constraints(session)
            if constraints:
                for constraint in constraints:
                    print(f"  • {constraint.get('name', 'N/A')}: {constraint.get('type', 'N/A')}")
            else:
                print("  No constraints found")
        except Exception as e:
            print(f"  Could not retrieve constraints: {e}")
        
        print("\n")
        
        # 6. Summary for quick reference
        print("6. QUICK REFERENCE SUMMARY")
        print("-" * 80)
        print("\nNode Labels:")
        for label_info in labels:
            print(f"  • {label_info['label']}")
        
        if relationships:
            print("\nRelationship Types:")
            for rel in relationships:
                print(f"  • {rel['relationship_type']}")
        else:
            print("\nRelationship Types:")
            print("  • None (no relationships in database)")
        
        print("\n")
        
        # 7. Generate example Cypher queries
        print("7. EXAMPLE CYPHER QUERIES")
        print("-" * 80)
        for label_info in labels[:3]:  # Show for top 3 labels
            label = label_info['label']
            print(f"\n  Get all {label} nodes:")
            print(f"  MATCH (n:{label}) RETURN n LIMIT 10")
            
            properties = get_properties_for_label(session, label)
            if properties:
                prop = properties[0]['key']
                print(f"\n  Search by {prop}:")
                print(f"  MATCH (n:{label}) WHERE n.{prop} = $value RETURN n")
        
        print("\n")
        print("=" * 80)
        print("INSPECTION COMPLETE")
        print("=" * 80)
    
    driver.close()


if __name__ == "__main__":
    main()
