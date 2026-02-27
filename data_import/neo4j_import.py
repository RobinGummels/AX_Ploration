from neo4j import GraphDatabase
import csv
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

buildings_path = 'buildings_for_neo4j_2.csv'
districts_path = 'districts_for_neo4j.csv'
functions_path = 'gebaeudefunktionen.csv'

BATCH_SIZE = 1000

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD),
    max_connection_lifetime=600,
    connection_timeout=30
)

# ---------------------
# Batch insert functions
# ---------------------
def insert_buildings(tx, batch):
    for row in batch:
        tx.run("""
        MERGE (b:Building {id: $id})
        SET b.area = $area,
            b.centroid = $centroid,
            b.floors_above = $floors_above,
            b.floors_below = $floors_below,
            b.street_name = $street_name,
            b.house_number = $house_number,
            b.name = $name,
            b.post_code = $post_code,
            b.geometry_geojson = $geometry_geojson
        """, **{
            "id": row.get("id"),
            "area": row.get("area"),
            "centroid": row.get("centroid"),
            "floors_above": int(row["floors_above"]) if row.get("floors_above") and row["floors_above"].strip() else None,
            "floors_below": int(row["floors_below"]) if row.get("floors_below") and row["floors_below"].strip() else None,
            "street_name": row.get("street_name"),
            "house_number": row.get("house_number"),
            "name": row.get("name"),
            "post_code": row.get("post_code"),
            "geometry_geojson": row.get("geometry_geojson"),
        })

def insert_districts(tx, batch):
    for row in batch:
        tx.run("""
        MERGE (d:District {gml_id: $gml_id})
        SET d.geometry_geojson = $geometry_geojson,
            d.Gemeinde_name = $Gemeinde_name,
            d.Gemeinde_schluessel = $Gemeinde_schluessel,
            d.Land_name = $Land_name,
            d.Land_schluessel = $Land_schluessel,
            d.Schluessel_gesamt = $Schluessel_gesamt,
            d.centroid = $centroid
        """, row)

def insert_functions(tx, batch):
    for row in batch:
        tx.run("""
        MERGE (f:Function {code: $code})
        ON CREATE SET 
            f.name = $name,
            f.description = $description
        ON MATCH SET 
            f.description = coalesce($description, f.description)
        """, **{
            "code": int(row.get("code")) if row.get("code") and row["code"].strip() else None,
            "name": row.get("name"),
            "description": row.get("description", "")
        })


def create_constraints(tx):
    tx.run("""
    CREATE CONSTRAINT IF NOT EXISTS
    FOR (f:Function)
    REQUIRE f.code IS UNIQUE
    """)
    tx.run("""
    CREATE CONSTRAINT IF NOT EXISTS
    FOR (b:Building)
    REQUIRE b.id IS UNIQUE
    """)
    tx.run("""
    CREATE CONSTRAINT IF NOT EXISTS
    FOR (d:District)
    REQUIRE d.gml_id IS UNIQUE
    """)


def import_csv(session, path, insert_func, delimiter=",", max_rows=None):
    batch = []
    counter = 0
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        reader.fieldnames = [h.strip().replace('\ufeff','') for h in reader.fieldnames]
        for row in reader:
            if max_rows and counter >= max_rows:
                break
            batch.append(row)
            counter += 1
            if len(batch) >= BATCH_SIZE:
                session.execute_write(insert_func, batch)
                batch = []
        if batch:
            session.execute_write(insert_func, batch)
    print("Imported", counter, "rows from", path)

def main():
    with driver.session() as session:
        session.execute_write(create_constraints)
        print("Constraints ensured")

        import_csv(session, buildings_path, insert_buildings)
        print("Buildings imported")

        import_csv(session, districts_path, insert_districts)
        print("Districts imported")

        import_csv(session, functions_path, insert_functions, delimiter=";")
        print("Functions imported")

    driver.close()

if __name__ == "__main__":
    main()
