# AX_Ploration API

> **REST API for Natural Language Queries on Berlin Building Data**
> 
> FastAPI-based HTTP server with Server-Sent Events (SSE) streaming support for real-time query processing updates.

---

## Quick Start

### Starting the Server

**Method 1: Using Docker** (Recommended)
```bash
# From project root
docker compose up --build
```

**Method 2: Direct Python**
```bash
# From project root
python -m backend.api.server

# Or with uvicorn directly
uvicorn backend.api.server:app --reload --host localhost --port 8000
```

**Server Starts On**: `http://localhost:8000`

---

## Endpoints

### 1. Health Check

**GET** `/`

Basic server status check.

**Response**:
```json
{
  "status": "online",
  "service": "AX_Ploration API",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

---

### 2. Detailed Health Check

**GET** `/health`

Checks server and Neo4j database connection.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 3. Query Buildings (Main Endpoint)

**POST** `/query`

Process natural language queries about Berlin buildings.

**Request Body**:
```json
{
  "query": "Show me alll Schools in Pankow",
  "stream": true,
  "spatial_filter": "POINT(388500 5819500)"
}
```

**Parameters**:
- `query` (string, required): Natural language query in any language
- `stream` (boolean, optional): Enable Server-Sent Events streaming (default: true)
- `spatial_filter` (string, optional): WKT geometry in EPSG:25833 for spatial filtering (either POINT or POLYGON)

#### Streaming Response (stream=true)

Returns Server-Sent Events with three event types:

**Event Type: message**
```json
{
  "type": "message",
  "content": "Identified attributes: ['area', 'floors_above']"
}
```

**Event Type: final**
```json
{
  "type": "final",
  "state": {
    "query": "Show me all Schools in Pankow",
    "attributes": ["area", "floors_above"],
    "building_functions": [1310, 1320],
    "building_function_names": ["Schule", "Schulgebäude"],
    "cypher_query": "MATCH (b:Building)-[:HAS_FUNCTION]->...",
    "results": [
      {
        "buildings": [...],
        "statistics": {
          "area_min": 456.78,
          "area_max": 3456.78,
          "area_mean": 1234.56,
          "floors_above_min": 1,
          "floors_above_max": 5,
          "floors_above_mean": 2.8,
          "house_number_min": 1,
          "house_number_max": 150,
          "building_count": 23
        }
      }
    ],
    "final_answer": "There are 23 Schools in Pankow...",
    "query_language": "English",
    "messages": ["Identified attributes...", "Generated Cypher...", ...]
  }
}
```

**Event Type: error**
```json
{
  "type": "error",
  "error": "Error during agent execution: ..."
}
```

**Example (Streaming)**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all Schools in Pankow",
    "stream": true
  }'
```

#### Non-Streaming Response (stream=false)

Returns complete final state as JSON.

**Response**:
```json
{
  "query": "Show me all Schools in Pankow",
  "query_language": "English",
  "attributes": ["area", "floors_above"],
  "needs_building_function": true,
  "building_function_query": "Schools",
  "building_functions": [1310, 1320],
  "building_function_names": ["Schule", "Schulgebäude"],
  "building_function_descriptions": ["Gebäude für Bildungszwecke", ...],
  "cypher_query": "MATCH (b:Building)-[:HAS_FUNCTION]->...",
  "results": [
    {
      "buildings": [
        {
          "id": "DEBE00YY11100066",
          "street_name": "Hauptstraße 12",
          "area": "1234.56",
          "floors_above": 3,
          "house_number": "12",
          "centroid": "POINT(388500 5819500)",
          "geometry_geojson": "{\"type\": \"MultiPolygon\", ...}",
          "function_code": 1310,
          "function_name": "Schule"
        }
      ],
      "statistics": {
        "area_min": 456.78,
        "area_max": 3456.78,
        "area_mean": 1234.56,
        "floors_above_min": 1,
        "floors_above_max": 5,
        "floors_above_mean": 2.8,
        "house_number_min": 1,
        "house_number_max": 150,
        "building_count": 23
      }
    }
  ],
  "spatial_comparison": null,
  "final_answer": "There are 23 School-Buildings in Pankow. The average area is 1.235 m²...",
  "error": null,
  "messages": [
    "Identified attributes: ['area', 'floors_above']",
    "Language: English",
    "Building function query: Schools",
    "Found 2 building functions via similarity search",
    "Generated Cypher query for district search",
    "Retrieved 23 buildings from database",
    "Calculated statistics for 23 buildings",
    "Generated answer for 1 results in English"
  ]
}
```

**Example (Non-Streaming)**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all hospitals",
    "stream": false
  }'
```

---

### 4. List Building Functions

**GET** `/functions`

List all available building functions from the database.

**Response**:
```json
{
  "count": 234,
  "functions": [
    {
      "code": 1000,
      "name": "Wohngebäude",
      "description": "Gebäude, das dem Wohnen dient"
    },
    {
      "code": 1010,
      "name": "Wohnhaus",
      "description": "Gebäude mit Wohnungen"
    },
    ...
  ]
}
```

**Example**:
```bash
curl http://localhost:8000/functions
```

---

## Spatial Filtering

The API supports three spatial filtering modes via the `spatial_filter` parameter:

### Mode 1: Polygon Containment

Filter buildings within a polygon boundary.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "All buildings in this area",
    "spatial_filter": "POLYGON((388000 5819000, 389000 5819000, 389000 5820000, 388000 5820000, 388000 5819000))",
    "stream": false
  }'
```

### Mode 2: Nearest X Buildings

Find the X nearest buildings to a point.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "The 5 nearest hospitals",
    "spatial_filter": "POINT(388500 5819500)",
    "stream": false
  }'
```

### Mode 3: Radius Search

Find all buildings within X meters of a point.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "All buildings in a radius of 500m",
    "spatial_filter": "POINT(388500 5819500)",
    "stream": false
  }'
```

**Important**: All coordinates must be in **EPSG:25833** (ETRS89/UTM Zone 33N), not WGS84!

---

## Multi-Language Support

The API automatically detects query language and responds accordingly:

**German Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Wie viele Schulen gibt es in Pankow?", "stream": false}'
```

**English Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all hospitals with more than 5 floors", "stream": false}'
```

**French Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Montrez-moi toutes les écoles", "stream": false}'
```

The `query_language` field in the response indicates the detected language.

---

## Response Structure

All responses include consistent structure:

### AgentState Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Original user query |
| `query_language` | string | Detected language (e.g., "German", "English") |
| `spatial_filter` | string | WKT geometry if provided |
| `attributes` | array | Identified building attributes |
| `needs_building_function` | boolean | Whether function lookup was needed |
| `building_function_query` | string | Extracted function terms |
| `building_functions` | array | Function codes (e.g., [1310, 1320]) |
| `building_function_names` | array | Function names (e.g., ["Schule", "Schulgebäude"]) |
| `building_function_descriptions` | array | Full descriptions |
| `cypher_query` | string | Generated Cypher query |
| `results` | array | Buildings with statistics: `[{"buildings": [...], "statistics": {...}}]` |
| `spatial_comparison` | object | Spatial filtering metadata (if applicable) |
| `final_answer` | string | Natural language response |
| `error` | string | Error message (null if successful) |
| `messages` | array | Processing step log |

### Building Object

Each building in `results[0].buildings`:

```json
{
  "id": "DEBE00YY11100066",
  "street_name": "Hauptstraße 12",
  "area": "1234.56",
  "floors_above": 3,
  "house_number": "12a",
  "centroid": "POINT(388500 5819500)",
  "geometry_geojson": "{\"type\": \"MultiPolygon\", ...}",
  "function_code": 1310,
  "function_name": "Schule"
}
```

### Statistics Object

Always included in `results[0].statistics`:

```json
{
  "area_min": 456.78,
  "area_max": 3456.78,
  "area_mean": 1234.56,
  "floors_above_min": 1,
  "floors_above_max": 5,
  "floors_above_mean": 2.8,
  "house_number_min": 1,
  "house_number_max": 150,
  "building_count": 23
}
```

---

## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (empty query)
- **500**: Internal Server Error (Neo4j connection, LLM error, etc.)

### Error Response

```json
{
  "detail": "Error processing query: ..."
}
```

### Common Errors

**Empty Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'

# Response: 400 Bad Request
{"detail": "Query cannot be empty"}
```

**Neo4j Connection Failed**:
```bash
# Check health endpoint
curl http://localhost:8000/health

# Response if database disconnected
{"status": "degraded", "database": "disconnected"}
```

---

## Configuration

The API server reads configuration from environment variables (`.env` file):

```bash
# Required
OPENAI_API_KEY=sk-...
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j

# Optional - API
API_PORT=8000
API_HOST=localhost

# Optional - LangSmith Tracing
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=ax_ploration
```

---

## CORS Configuration

CORS is enabled for all origins:

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

For production, restrict `allow_origins` to your frontend domain.

---

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your credentials

# Start server
python -m backend.api.server

# Or with hot reload
uvicorn backend.api.server:app --reload --host localhost --port 8000
```

### Testing Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Basic Query**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query", "stream": false}'
```

**Streaming (Watch Live)**:
```bash
curl -N -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Zeige mir alle Schulen", "stream": true}'
```

---

## Docker Deployment

### Using Docker Compose

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Docker Configuration

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  ax-ploration:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ax-ploration-api
    ports:
      - "${API_PORT:-8000}:${API_PORT:-8000}"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USERNAME=${NEO4J_USERNAME}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - API_PORT=${API_PORT:-8000}
      - API_HOST=0.0.0.0
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${API_PORT:-8000}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Further Reading

- **Scripts Documentation**: See [backend/README.md](../README.md) for detailed agent workflow
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Server-Sent Events**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

---

## Support

For technical details on the agent workflow, see the [Scripts README](../README.md).

For API issues, check:
1. Server logs: `docker compose logs -f`
2. Health endpoint: `GET /health`
3. Environment configuration: Verify `.env` file
