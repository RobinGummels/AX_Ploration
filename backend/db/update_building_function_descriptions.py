#!/usr/bin/env python3
"""Update BuildingFunction descriptions in Neo4j from CSV.

Reads the semicolon-delimited building_functions.csv and updates existing
BuildingFunction nodes in Neo4j with the description field.
"""

import argparse
import csv
import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from neo4j import GraphDatabase


def load_config() -> Dict[str, str]:
    """Load required Neo4j configuration from environment variables."""
    load_dotenv()

    config = {
        "uri": os.getenv("NEO4J_URI"),
        "user": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD"),
        "database": os.getenv("NEO4J_DATABASE", "neo4j"),
    }

    missing = [k for k, v in config.items() if v in (None, "") and k != "database"]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return config


def read_functions(csv_path: Path) -> List[Dict[str, str]]:
    """Read building functions from semicolon-delimited CSV."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        required = {"code", "name", "description"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV headers must include: {', '.join(sorted(required))}")
        rows = [row for row in reader]

    return rows


def update_descriptions(driver, database: str, functions: List[Dict[str, str]]):
    """Update description property on existing BuildingFunction nodes.

    Matches the actual label (:Functions) and compares the code using string semantics
    to handle differing property types (string/int). Keeps :BuildingFunction/:Function
    as fallbacks for robustness.
    """

    def _update(tx, code_str: str, description: str):
        query = (
            "MATCH (f) "
            "WHERE (f:Functions OR f:BuildingFunction OR f:Function) "
            "  AND toString(f.code) = $code "
            "SET f.description = $description "
            "RETURN f.code AS code, labels(f) AS labels"
        )
        return tx.run(query, code=code_str, description=description).single()

    updated = 0
    missing = []

    with driver.session(database=database) as session:
        for row in functions:
            code_str = row.get("code", "").strip()
            desc = row.get("description", "").strip()
            if not code_str:
                continue

            result = session.execute_write(_update, code_str, desc)
            if result:
                updated += 1
            else:
                missing.append(code_str)

    return updated, missing


def inspect_database(driver, database: str):
    """Print basic info about BuildingFunction/Function nodes for debugging."""
    with driver.session(database=database) as session:
        counts = session.run(
            """
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(*) AS count
            ORDER BY count DESC
            LIMIT 25
            """
        ).data()

        print("Label counts (top 25):")
        for row in counts:
            print(f"  {row['label']}: {row['count']}")

        sample = session.run(
            """
            MATCH (f)
            WHERE f.code IS NOT NULL
            WITH f LIMIT 5
            RETURN labels(f) AS labels, keys(f) AS keys, f.code AS code, f.name AS name, f.description AS description
            """
        ).data()
        print("\nSample nodes with property 'code' (up to 5):")
        for row in sample:
            print(f"  labels={row['labels']}, keys={row['keys']}, code={row['code']}, name={row['name']}, description={row['description']}")


def main():
    parser = argparse.ArgumentParser(description="Update BuildingFunction descriptions in Neo4j from CSV")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(__file__).parent.parent / "objektartenkatalogExtraction" / "building_functions.csv",
        help="Path to semicolon-delimited building_functions.csv",
    )
    parser.add_argument(
        "--inspect-only",
        action="store_true",
        help="Only inspect database contents and exit",
    )
    args = parser.parse_args()

    config = load_config()
    functions = read_functions(args.csv)

    print(f"Read {len(functions)} building functions from {args.csv}")

    driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
    try:
        if args.inspect_only:
            inspect_database(driver, config["database"])
            return

        inspect_database(driver, config["database"])
        updated, missing = update_descriptions(driver, config["database"], functions)
    finally:
        driver.close()

    print(f"Updated descriptions for {updated} nodes")
    if missing:
        print(f"Warning: {len(missing)} codes not found in DB: {sorted(missing)[:10]}{' ...' if len(missing) > 10 else ''}")


if __name__ == "__main__":
    main()
