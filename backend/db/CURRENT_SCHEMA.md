# Neo4j Database Schema - Current State

## Node Labels

### 1. Buildings (197,862 nodes)
**Properties:**
- `id`: STRING NOT NULL - Unique identifier (e.g., "DEBE00YY11100066")
- `centroid`: STRING NOT NULL - Point format: "Point (x y)" in EPSG:25833
- `floors_above`: INTEGER NOT NULL - Number of floors above ground
- `street_name`: STRING NOT NULL - Street name
- `geometry_geojson`: STRING NOT NULL - MULTIPOLYGON geometry
- `house_number`: STRING (optional) - House number
- `post_code`: STRING (optional) - Postal code
- `IN_DISTRICT`: STRING NOT NULL - District name (property, not just relationship!)
- `HAS_FUNCTION`: INTEGER NOT NULL - Function code (property, not just relationship!)

### 2. Functions (234 nodes)
**Properties:**
- `code`: INTEGER NOT NULL - Unique function code (e.g., 1000, 1010)
- `name`: STRING NOT NULL - Function name (e.g., "Wohngebäude")
- `description`: STRING NOT NULL - Full description
- `description_embedding_small`: LIST<FLOAT> NOT NULL - Embedding from text-embedding-3-small
- `description_embedding_large`: LIST<FLOAT> NOT NULL - Embedding from text-embedding-3-large

### 3. Districts (12 nodes)
**Properties:**
- `Gemeinde_name`: STRING NOT NULL - District name (e.g., "Reinickendorf")
- `Gemeinde_schluessel`: INTEGER NOT NULL - District key
- `Land_name`: STRING NOT NULL - State name (always "Berlin")
- `Land_schluessel`: INTEGER NOT NULL - State key
- `Schluessel_gesamt`: INTEGER NOT NULL - Combined key
- `gml_id`: STRING NOT NULL - GML identifier
- `WKT`: STRING NOT NULL - MULTIPOLYGON geometry in WKT format
- `centroid`: STRING NOT NULL - Point format: "Point (lon lat)" in WGS84!

## Relationships

### 1. (Buildings)-[:IN_DISTRICT]->(Districts) - 198,044 instances
Buildings are connected to their district

### 2. (Buildings)-[:HAS_FUNCTION]->(Functions) - 197,862 instances
Buildings are connected to their function type

### 3. (Functions)-[:HAS_SUBFUNCTION]->(Functions) - 223 instances
Functions can have subfunctions (hierarchical structure)

## Key Changes from Old Schema

### CRITICAL DIFFERENCES:

1. **Label Names Changed:**
   - OLD: `Building` → NEW: `Buildings`
   - OLD: `BuildingFunction` → NEW: `Functions`
   - OLD: `District` → NEW: `Districts`

2. **Property Names Changed:**
   - OLD: `floorAbove` → NEW: `floors_above`
   - OLD: `houseNumber` → NEW: `house_number`
   - OLD: `streetName` → NEW: `street_name`
   - OLD: `geometryGeojson` → NEW: `geometry_geojson`
   - OLD: `postCode` → NEW: `post_code` (now exists!)

3. **RELATIONSHIPS NOW EXIST!**
   - OLD: No relationships
   - NEW: Buildings have :IN_DISTRICT and :HAS_FUNCTION relationships
   - NEW: Functions have :HAS_SUBFUNCTION relationships

4. **Dual Storage Pattern:**
   - Buildings have BOTH properties AND relationships:
     - Property `IN_DISTRICT` (string: district name)
     - Relationship `-[:IN_DISTRICT]->` (to Districts node)
     - Property `HAS_FUNCTION` (integer: function code)
     - Relationship `-[:HAS_FUNCTION]->` (to Functions node)

5. **District Properties:**
   - NEW: `Gemeinde_name` instead of `municipalityName`
   - NEW: `Land_name` instead of `stateName`
   - NEW: `WKT` instead of `wkt`
   - District centroids are in WGS84 (lon/lat), not EPSG:25833!

6. **Function Properties:**
   - NEW: Embeddings are now present (`description_embedding_small`, `description_embedding_large`)

7. **Coordinate Systems:**
   - Buildings centroid: EPSG:25833 (UTM) - "Point (x y)"
   - Districts centroid: WGS84 (lon/lat) - "Point (lon lat)"

## Query Pattern Examples

### Get building with function name:
```cypher
MATCH (b:Buildings)-[:HAS_FUNCTION]->(f:Functions)
WHERE f.name = 'Wohngebäude'
RETURN b
```

### Get buildings in district:
```cypher
MATCH (b:Buildings)-[:IN_DISTRICT]->(d:Districts)
WHERE d.Gemeinde_name = 'Mitte'
RETURN b
```

### Get building with both function and district:
```cypher
MATCH (b:Buildings)-[:HAS_FUNCTION]->(f:Functions),
      (b)-[:IN_DISTRICT]->(d:Districts)
WHERE f.name = 'Wohngebäude' 
  AND d.Gemeinde_name = 'Mitte'
RETURN b, f, d
```

### Search functions by embedding (needs vector index):
```cypher
// Requires vector index on Functions.description_embedding_small
CALL db.index.vector.queryNodes('function_embeddings', 5, $embedding)
YIELD node, score
RETURN node, score
```

## Indexes & Constraints

### Unique Constraints:
- Buildings.id (UNIQUENESS)
- Functions.code (UNIQUENESS)
- Districts.Gemeinde_name (UNIQUENESS)

### Indexes:
- RANGE indexes on all unique constraint fields
- LOOKUP indexes available
