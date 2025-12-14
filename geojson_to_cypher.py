import json
import csv

def buildings_to_cypher(geojson_path, output_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    cypher_lines = []

    for feature in geojson_data['features']:
        properties = feature.get('properties', {})
        # geometry = feature.get('geometry', {})

        uuid = properties.get('uuid', 'unknown_uuid')
        name = properties.get('nam', 'unknown_name')
        house_number = properties.get('hnr', 'unknown_house_number')
        post_code = properties.get('pnr', 'unknown_postcode')
        area = properties.get('area', 'unknown_area')
        floors_above = properties.get('aog', 'unknown_floors_above')
        floors_below = properties.get('aug', 'unknown_floors_below')
        centroid = properties.get('centroid', {})

        ortsteil = properties.get('Gemeinde_name', 'unknown_ortsteil')
        gfk = properties.get('gfk', 'unknown_gfk')

        cypher_lines.append(
            f"CREATE (b:Building {{ "
            f"uuid: '{uuid}', "
            f"name: '{name}', "
            f"house_number: '{house_number}', "
            f"post_code: '{post_code}', "
            f"area: '{area}', "
            f"floors_above: '{floors_above}', "
            f"floors_below: '{floors_below}', "
            f"centroid: '{centroid}' "
            f"}});"
        )

        if gfk and gfk != 'unknown_gfk':
            cypher_lines.append(
                f"MATCH (b:Building {{uuid: '{uuid}'}}), (f:Function {{code: '{gfk}'}}) "
                f"CREATE (b)-[:HAS_FUNCTION]->(f);"
            )

        if ortsteil and ortsteil != 'unknown_ortsteil':
            cypher_lines.append(
                f"MATCH (b:Building {{uuid: '{uuid}'}}), (d:District {{name: '{ortsteil}'}}) "
                f"CREATE (b)-[:IN_DISTRICT]->(d);"
            )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(cypher_lines))

def bezirke_to_cypher(geojson_path, output_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    cypher_lines = []

    for feature in geojson_data['features']:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        name = properties.get('Gemeinde_name', 'unknown_name')
        centroid = properties.get('centroid', {})

        # Convert to safe JSON
        geometry_json = json.dumps(geometry)
        centroid_json = json.dumps(centroid)

        # Escape single quotes in name
        name = name.replace("'", "\\'")

        cypher_lines.append(
            f"CREATE (d:District {{ "
            f"name: '{name}', "
            f"centroid: '{centroid_json}', "
            f"geometry: '{geometry_json}' "
            f"}});"
        )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(cypher_lines))

def functions_to_cypher(csv_path, output_path):
    cypher_lines = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')

        for row in reader:
            name = row.get('name', '').strip()
            code = row.get('code', '').strip()
            description = row.get('description', '').strip()

            if name:
                cypher_lines.append(
                    f"CREATE (f:Function {{ name: '{name}', code: '{code}', description: '{description}' }});"
                )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(cypher_lines))


# functions_to_cypher('gebaeudefunktionen.csv', 'functions.cypher')
# bezirke_to_cypher('bezirksgrenzen_with_centroid.geojson', 'districts.cypher')
buildings_to_cypher('gebaeude_berlin_without_bauteile_with_area_ortsteil_centroid.geojson', 'buildings.cypher')
