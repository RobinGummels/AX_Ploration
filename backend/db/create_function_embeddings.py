#!/usr/bin/env python3
"""Create embeddings for BuildingFunction descriptions in Neo4j.

Reads all Functions nodes from Neo4j, creates embeddings using OpenAI's
text-embedding-3-small and text-embedding-3-large models, and stores them
as description_embedding_small and description_embedding_large properties.
"""

import argparse
import os
import time
from typing import List, Dict, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI


def load_config() -> Dict[str, str]:
    """Load required configuration from environment variables."""
    load_dotenv()

    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "neo4j_uri": os.getenv("NEO4J_URI"),
        "neo4j_user": os.getenv("NEO4J_USERNAME", "neo4j"),
        "neo4j_password": os.getenv("NEO4J_PASSWORD"),
        "neo4j_database": os.getenv("NEO4J_DATABASE", "neo4j"),
    }

    missing = [k for k, v in config.items() if v in (None, "")]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return config


def fetch_functions(driver, database: str) -> List[Dict]:
    """Fetch all Functions nodes with code, name, and description."""
    with driver.session(database=database) as session:
        result = session.run(
            """
            MATCH (f:Functions)
            WHERE f.description IS NOT NULL
            RETURN f.code AS code, f.name AS name, f.description AS description
            ORDER BY f.code
            """
        )
        return [dict(record) for record in result]


def create_embedding(client: OpenAI, text: str, model: str, max_retries: int = 3) -> Optional[List[float]]:
    """Create embedding with retry logic."""
    for attempt in range(max_retries):
        try:
            response = client.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"  Retry {attempt + 1}/{max_retries} after {wait_time}s due to: {e}")
                time.sleep(wait_time)
            else:
                print(f"  Failed after {max_retries} attempts: {e}")
                return None


def update_embeddings(
    driver,
    database: str,
    openai_client: OpenAI,
    functions: List[Dict],
    small_model: str,
    large_model: str,
    skip_existing: bool = True
):
    """Create and store embeddings for all functions."""
    
    def _update(tx, code: int, embedding_small: List[float], embedding_large: List[float]):
        query = """
        MATCH (f:Functions)
        WHERE f.code = $code
        SET f.description_embedding_small = $embedding_small,
            f.description_embedding_large = $embedding_large
        RETURN f.code AS code
        """
        return tx.run(
            query,
            code=code,
            embedding_small=embedding_small,
            embedding_large=embedding_large
        ).single()

    def _check_existing(tx, code: int):
        query = """
        MATCH (f:Functions)
        WHERE f.code = $code
        RETURN f.description_embedding_small IS NOT NULL AS has_small,
               f.description_embedding_large IS NOT NULL AS has_large
        """
        result = tx.run(query, code=code).single()
        return result["has_small"] and result["has_large"] if result else False

    updated = 0
    skipped = 0
    failed = []

    total = len(functions)
    
    with driver.session(database=database) as session:
        for idx, func in enumerate(functions, 1):
            code = func["code"]
            description = func["description"]
            name = func["name"]
            
            print(f"\n[{idx}/{total}] Processing {code} - {name}")
            
            # Check if embeddings already exist
            if skip_existing:
                has_embeddings = session.execute_read(_check_existing, code)
                if has_embeddings:
                    print(f"  ✓ Embeddings already exist, skipping")
                    skipped += 1
                    continue
            
            # Create embeddings
            print(f"  Creating small embedding ({small_model})...")
            embedding_small = create_embedding(openai_client, description, small_model)
            
            if not embedding_small:
                print(f"  ✗ Failed to create small embedding")
                failed.append((code, name, "small embedding failed"))
                continue
            
            print(f"  Creating large embedding ({large_model})...")
            embedding_large = create_embedding(openai_client, description, large_model)
            
            if not embedding_large:
                print(f"  ✗ Failed to create large embedding")
                failed.append((code, name, "large embedding failed"))
                continue
            
            # Store embeddings
            print(f"  Storing embeddings in Neo4j...")
            result = session.execute_write(_update, code, embedding_small, embedding_large)
            
            if result:
                print(f"  ✓ Successfully updated node")
                updated += 1
            else:
                print(f"  ✗ Failed to update node in database")
                failed.append((code, name, "database update failed"))
            
            # Small delay to respect rate limits
            if idx < total:
                time.sleep(0.1)
    
    return updated, skipped, failed


def main():
    parser = argparse.ArgumentParser(
        description="Create embeddings for BuildingFunction descriptions in Neo4j"
    )
    parser.add_argument(
        "--small-model",
        type=str,
        default="text-embedding-3-small",
        help="OpenAI embedding model for small embeddings",
    )
    parser.add_argument(
        "--large-model",
        type=str,
        default="text-embedding-3-large",
        help="OpenAI embedding model for large embeddings",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-creation of embeddings even if they already exist",
    )
    args = parser.parse_args()

    config = load_config()
    
    # Initialize clients
    openai_client = OpenAI(api_key=config["openai_api_key"])
    neo4j_driver = GraphDatabase.driver(
        config["neo4j_uri"],
        auth=(config["neo4j_user"], config["neo4j_password"])
    )

    try:
        # Fetch functions
        print("Fetching Functions nodes from Neo4j...")
        functions = fetch_functions(neo4j_driver, config["neo4j_database"])
        print(f"Found {len(functions)} functions with descriptions\n")
        
        if not functions:
            print("No functions found. Exiting.")
            return 0
        
        # Create embeddings
        print(f"Creating embeddings using:")
        print(f"  Small model: {args.small_model}")
        print(f"  Large model: {args.large_model}")
        print(f"  Skip existing: {not args.force}")
        print("=" * 60)
        
        updated, skipped, failed = update_embeddings(
            neo4j_driver,
            config["neo4j_database"],
            openai_client,
            functions,
            args.small_model,
            args.large_model,
            skip_existing=not args.force
        )
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total functions: {len(functions)}")
        print(f"Successfully updated: {updated}")
        print(f"Skipped (already exist): {skipped}")
        print(f"Failed: {len(failed)}")
        
        if failed:
            print("\nFailed items:")
            for code, name, reason in failed[:10]:
                print(f"  {code} - {name}: {reason}")
            if len(failed) > 10:
                print(f"  ... and {len(failed) - 10} more")
        
        print("\nEmbedding creation completed!")
        return 0 if not failed else 1
        
    finally:
        neo4j_driver.close()


if __name__ == "__main__":
    exit(main())
