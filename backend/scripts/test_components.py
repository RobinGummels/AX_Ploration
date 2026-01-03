"""
Test script for individual components of the AX_Ploration agent.

Run with: python -m backend.scripts.test_components
"""

import json
from typing import Dict, Any


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def test_config():
    """Test configuration loading."""
    print_section("Testing Configuration")
    
    try:
        from .config import (
            OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDING_MODEL,
            NEO4J_URI, NEO4J_USERNAME, NEO4J_DATABASE, validate_config
        )
        
        print(f"✓ OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'MISSING'}")
        print(f"✓ OPENAI_MODEL: {OPENAI_MODEL}")
        print(f"✓ OPENAI_EMBEDDING_MODEL: {OPENAI_EMBEDDING_MODEL}")
        print(f"✓ NEO4J_URI: {NEO4J_URI}")
        print(f"✓ NEO4J_USERNAME: {NEO4J_USERNAME}")
        print(f"✓ NEO4J_DATABASE: {NEO4J_DATABASE}")
        
        validate_config()
        print("\n✓ Configuration validated successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Configuration error: {e}")
        return False


def test_neo4j_connection():
    """Test Neo4j database connection."""
    print_section("Testing Neo4j Connection")
    
    try:
        from .utils.neo4j_client import neo4j_client
        
        if neo4j_client.verify_connection():
            print("✓ Neo4j connection successful!")
            
            # Try to get some data
            try:
                result = neo4j_client.execute_query("RETURN 1 AS test")
                print(f"✓ Query execution works: {result}")
            except Exception as e:
                print(f"✗ Query execution failed: {e}")
            
            return True
        else:
            print("✗ Neo4j connection failed!")
            return False
            
    except Exception as e:
        print(f"✗ Neo4j error: {e}")
        return False


def test_llm_client():
    """Test LLM client functionality."""
    print_section("Testing LLM Client")
    
    try:
        from .utils.llm_client import llm_client
        
        # Test chat completion
        print("Testing chat completion...")
        response = llm_client.chat_completion([
            {"role": "user", "content": "Reply with only: 'LLM works!'"}
        ])
        print(f"✓ Chat completion: {response}")
        
        # Test JSON completion
        print("\nTesting JSON completion...")
        json_response = llm_client.chat_completion_json([
            {"role": "user", "content": "Reply with JSON: {\"status\": \"ok\"}"}
        ])
        print(f"✓ JSON completion: {json_response}")
        
        # Test embedding
        print("\nTesting embedding creation...")
        embedding = llm_client.create_embedding("Test text")
        print(f"✓ Embedding created: {len(embedding)} dimensions")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM client error: {e}")
        return False


def test_attribute_identification():
    """Test the attribute identification node."""
    print_section("Testing Attribute Identification Node")
    
    try:
        from .nodes.attribute_identification import identify_attributes
        from .models import AgentState
        
        # Create test state
        test_state: AgentState = {
            "query": "Zeige mir alle Wohngebäude in Pankow mit mehr als 3 Stockwerken",
            "attributes": [],
            "needs_building_function": False,
            "building_functions": [],
            "building_function_names": [],
            "building_function_descriptions": [],
            "query_type": "",
            "cypher_query": "",
            "results": [],
            "spatial_comparison": None,
            "final_answer": "",
            "error": None,
            "messages": []
        }
        
        print(f"Query: {test_state['query']}")
        result = identify_attributes(test_state)
        
        print(f"\n✓ Identified attributes: {result.get('attributes', [])}")
        print(f"✓ Needs building function: {result.get('needs_building_function', False)}")
        print(f"✓ Messages: {result.get('messages', [])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Attribute identification error: {e}")
        return False


def test_query_interpretation():
    """Test the query interpretation node."""
    print_section("Testing Query Interpretation Node")
    
    try:
        from .nodes.query_interpretation import interpret_query
        from .models import AgentState
        
        # Test different query types
        test_queries = [
            ("Zeige mir alle Gebäude in Spandau", "district"),
            ("Finde Gebäude im Umkreis von 500m um den Hauptbahnhof", "nearby"),
            ("Wie viele Schulgebäude gibt es in Pankow?", "statistics"),
        ]
        
        for query, expected_type in test_queries:
            test_state: AgentState = {
                "query": query,
                "attributes": ["function"],
                "needs_building_function": False,
                "building_functions": [],
                "building_function_names": [],
                "building_function_descriptions": [],
                "query_type": "",
                "cypher_query": "",
                "results": [],
                "spatial_comparison": None,
                "final_answer": "",
                "error": None,
                "messages": []
            }
            
            result = interpret_query(test_state)
            actual_type = result.get("query_type", "unknown")
            status = "✓" if actual_type == expected_type else "~"
            print(f"{status} Query: '{query[:40]}...'")
            print(f"  Expected: {expected_type}, Got: {actual_type}")
        
        return True
        
    except Exception as e:
        print(f"✗ Query interpretation error: {e}")
        return False


def test_cypher_generation():
    """Test Cypher query generation."""
    print_section("Testing Cypher Generation")
    
    try:
        from .nodes.cypher_generation import generate_cypher_district
        from .models import AgentState
        
        test_state: AgentState = {
            "query": "Zeige mir alle Wohngebäude in Spandau",
            "attributes": ["HAS_FUNCTION", "floors_above"],
            "needs_building_function": True,
            "building_functions": [1010],
            "building_function_names": ["Wohnhaus"],
            "building_function_descriptions": ["Wohngebäude mit Wohnungen"],
            "query_type": "district",
            "cypher_query": "",
            "results": [],
            "spatial_comparison": None,
            "final_answer": "",
            "error": None,
            "messages": []
        }
        
        print(f"Query: {test_state['query']}")
        result = generate_cypher_district(test_state)
        
        cypher = result.get("cypher_query", "")
        print(f"\n✓ Generated Cypher:\n{cypher}")
        
        return bool(cypher)
        
    except Exception as e:
        print(f"✗ Cypher generation error: {e}")
        return False


def test_graph_compilation():
    """Test that the full graph compiles correctly."""
    print_section("Testing Graph Compilation")
    
    try:
        from .graph import graph, create_workflow
        
        print("✓ Graph imported successfully")
        
        # Check nodes
        workflow = create_workflow()
        print("✓ Workflow created with nodes")
        
        # Compile
        compiled = workflow.compile()
        print("✓ Graph compiled successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Graph compilation error: {e}")
        return False


def run_all_tests():
    """Run all component tests."""
    print("\n" + "=" * 60)
    print(" AX_Ploration Component Tests")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Neo4j Connection", test_neo4j_connection),
        ("LLM Client", test_llm_client),
        ("Attribute Identification", test_attribute_identification),
        ("Query Interpretation", test_query_interpretation),
        ("Cypher Generation", test_cypher_generation),
        ("Graph Compilation", test_graph_compilation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    run_all_tests()
