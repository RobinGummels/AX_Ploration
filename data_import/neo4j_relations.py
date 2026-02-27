from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

BATCH_SIZE = 5000

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD),
    max_connection_lifetime=600,
    connection_timeout=30
)


import csv
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD),
    max_connection_lifetime=600,
    connection_timeout=30
)


def create_building_relations_from_csv(session, csv_path: str):
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        counter_districts = 0
        counter_functions = 0

        for row in reader:
            # print(row)
            b_id = row.get("id", "").strip()
            func = int(row.get("HAS_FUNCTION", "").strip())
            dist = row.get("IN_DISTRICT", "").strip()

            if not b_id:
                continue

            # HAS_FUNCTION
            if func:
                session.run(
                    """
                    MATCH (b:Building {id: $id})
                    MATCH (f:Function {code: $code})
                    MERGE (b)-[:HAS_FUNCTION]->(f)
                    """,
                    id=b_id,
                    code=func,
                )
                counter_functions += 1

            # IN_DISTRICT
            if dist:
                session.run(
                    """
                    MATCH (b:Building {id: $id})
                    MATCH (d:District {Gemeinde_name: $name})
                    MERGE (b)-[:IN_DISTRICT]->(d)
                    """,
                    id=b_id,
                    name=dist,
                )
                counter_districts += 1

    print(f"Created {counter_functions} HAS_FUNCTION relationships.")
    print(f"Created {counter_districts} IN_DISTRICT relationships.")

def get_parent_function_code(code: int) -> int | None:
    factor = 1
    temp = code
    while temp > 0:
        digit = temp % 10
        if digit != 0:
            parent = code - digit * factor
            return parent if parent != code else None
        factor *= 10
        temp //= 10
    return None

def create_function_hierarchy_relations(session):
    with session:
        result = session.run("MATCH (f:Function) RETURN f.code AS code")
        codes = [record["code"] for record in result]

        counter = 0

        for code in codes:
            parent_code = get_parent_function_code(code)
            if parent_code is None:
                continue

            record = session.run(
                "MATCH (parent:Function {code: $parent}), (child:Function {code: $child}) "
                "RETURN parent, child",
                parent=parent_code,
                child=code
            ).single()

            if record:
                session.run(
                    "MATCH (parent:Function {code: $parent}), (child:Function {code: $child}) "
                    "MERGE (parent)-[:HAS_SUBFUNCTION]->(child)",
                    parent=parent_code,
                    child=code
                )

                counter += 1
        print(f"Created {counter} HAS_SUBFUNCTION relationships.")


def delete_building_relations(session, batch_size: int = 5000):
    while True:
        result = session.run(
            """
            MATCH (b:Building)-[r]->()
            WITH r
            LIMIT $batch_size
            DELETE r
            RETURN count(r) AS c
            """,
            batch_size=batch_size,
        )
        c = result.single()["c"]
        print(f"Deleted {c} building relations")
        if c == 0:
            break

def delete_functions_hierarchy_relations(session):
    session.run(
        """
        MATCH (:Function)-[r:HAS_SUBFUNCTION]->(:Function)
        DELETE r
        """
    )
    print("All HAS_SUBFUNCTION relationships deleted.")


def main():
    with driver.session() as session:
        delete_building_relations(session)
        # delete_functions_hierarchy_relations(session)
        create_building_relations_from_csv(session, "buildings_for_neo4j.csv")
        # create_function_hierarchy_relations(session)
    driver.close()


if __name__ == "__main__":
    main()
