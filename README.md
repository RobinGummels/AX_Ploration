# AX_Ploration

AX_Ploration is an AI-assisted application for querying ALKIS building data (AX_Gebaeude features) using natural language. This project is part of the "Spatial Information Search" course at University of Münster (WiSe 25/26).

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Backend Scripts](#backend-scripts)
- [REST API](#rest-api)
- [Frontend Integration](#frontend-integration)
- [Docker Deployment](#docker-deployment)
- [Additional Tools](#additional-tools)

## Overview

The system uses a LangGraph-based agent that processes natural language queries in German and converts them into Cypher queries to retrieve building data from a Neo4j database containing Berlin ALKIS data (96,572 buildings, 234 building functions, 12 districts).

**Key Technologies:**
- LangGraph for agent workflow orchestration
- OpenAI GPT-4o for natural language understanding
- Neo4j for graph database storage
- FastAPI for REST API with Server-Sent Events streaming
- Docker for containerized deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Neo4j database (Aura or local instance)
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AX_Ploration
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables by creating a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
API_PORT=8000
```

### Run with Docker (Recommended)

```bash
# Build and start the API server
docker-compose up --build

# The API will be available at http://localhost:8000
```

### Run Locally

```bash
# Start the API server
python -m backend.api.server

# Or use the CLI directly
python -m backend.scripts.main "Wie viele Gebäude gibt es in Mitte?"
```

## Project Structure

```
AX_Ploration/
├── backend/
│   ├── scripts/          # Core agent implementation
│   └── api/              # REST API with streaming support
├── sample-scripts/       # Jupyter notebook examples
├── docker-compose.yml    # Docker deployment configuration
├── Dockerfile           # Container image definition
└── requirements.txt     # Python dependencies
```

## Backend Scripts

The `backend/scripts/` directory contains the core LangGraph agent implementation for direct programmatic use.

### Command Line Interface

Run queries directly from the command line:

```bash
# Basic query
python -m backend.scripts.main "Zeige mir alle Wohngebäude in Mitte"

# Verbose mode (shows processing steps)
python -m backend.scripts.main "Wie viele Schulen gibt es?" --verbose
```

### Programmatic Usage

```python
from backend.scripts.graph import graph
from backend.scripts.main import create_initial_state

# Execute a query
initial_state = create_initial_state("Zeige mir alle Krankenhäuser")
result = graph.invoke(initial_state)

print(result["final_answer"])
print(f"Query Type: {result['query_type']}")
print(f"Results: {len(result['results'])}")
```

### Agent Workflow

The agent processes queries through these stages:

1. **Attribute Identification** - Extracts requested building attributes
2. **Embedding Search** - Finds matching building functions (if needed)
3. **Query Interpretation** - Classifies query type (district/nearby/statistics)
4. **Cypher Generation** - Creates appropriate database query
5. **Data Retrieval** - Executes query against Neo4j
6. **Spatial Comparison** - Performs spatial analysis (for location-based queries)
7. **Answer Generation** - Formats natural language response

For detailed documentation, see [backend/README.md](backend/README.md).

## REST API

The `backend/api/` directory provides a FastAPI-based REST API with streaming support, enabling real-time query processing updates.

### Starting the API Server

**Option 1: Docker (Recommended)**
```bash
docker-compose up --build
```

**Option 2: Local**
```bash
python -m backend.api.server
```

**Option 3: Custom Configuration**
```bash
# Set port in .env
echo "API_PORT=5000" >> .env
python -m backend.api.server
```

### API Endpoints

#### POST /query

Process natural language queries with optional streaming.

**Request:**
```json
{
  "query": "Wie viele Gebäude gibt es in Mitte?",
  "stream": true
}
```

**Response (Streaming mode):**

Server-Sent Events stream with incremental updates:

```
data: {"type": "message", "content": "Identified attributes: ['Gebäudeanzahl']"}

data: {"type": "message", "content": "Query type: district"}

data: {"type": "message", "content": "Generated Cypher query for cypher_district"}

data: {"type": "final", "state": {
  "query": "Wie viele Gebäude gibt es in Mitte?",
  "attributes": ["Gebäudeanzahl"],
  "query_type": "district",
  "cypher_query": "MATCH (b:Building)-[:IN_DISTRICT]->(d:District)...",
  "results": [{"Gebäudeanzahl": 20746}],
  "final_answer": "In Mitte gibt es insgesamt 20.746 Gebäude.",
  "messages": [...]
}}
```

**Response (Non-streaming mode):**

Complete AgentState as JSON:

```json
{
  "query": "Wie viele Gebäude gibt es in Mitte?",
  "attributes": ["Gebäudeanzahl"],
  "needs_building_function": false,
  "building_functions": [],
  "query_type": "district",
  "cypher_query": "MATCH (b:Building)-[:IN_DISTRICT]->(d:District)\nWHERE d.Gemeinde_name = 'Mitte'\nRETURN count(b) AS Gebäudeanzahl",
  "results": [{"Gebäudeanzahl": 20746}],
  "final_answer": "In Mitte gibt es insgesamt 20.746 Gebäude.",
  "messages": [...]
}
```

#### GET /health

Check API and database connectivity:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### GET /functions

List all available building functions:

```bash
curl http://localhost:8000/functions
```


## Frontend Integration

### JavaScript Fetch API (Non-streaming)

```javascript
async function queryBuildings(query) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      stream: false
    })
  });
  
  const data = await response.json();
  console.log('Answer:', data.final_answer);
  console.log('Results:', data.results);
  return data;
}

// Usage
queryBuildings('Wie viele Schulen gibt es in Berlin?');
```

### JavaScript EventSource (Streaming)

```javascript
function streamQuery(query) {
  const messages = [];
  let finalState = null;
  
  const eventSource = new EventSource(
    `http://localhost:8000/query?` + 
    new URLSearchParams({
      query: query,
      stream: 'true'
    })
  );
  
  // Alternative: Use fetch with POST
  fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      stream: true
    })
  }).then(async response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      
      const text = decoder.decode(value);
      const lines = text.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          
          if (data.type === 'message') {
            console.log('Progress:', data.content);
            messages.push(data.content);
            // Update UI with progress message
            updateProgressUI(data.content);
          } 
          else if (data.type === 'final') {
            console.log('Final answer:', data.state.final_answer);
            finalState = data.state;
            // Update UI with final results
            displayResults(data.state);
          }
          else if (data.type === 'error') {
            console.error('Error:', data.error);
            displayError(data.error);
          }
        }
      }
    }
  });
}

// Usage
streamQuery('Zeige mir alle Wohngebäude in Mitte');
```

## Docker Deployment

### Building and Running

```bash
# Build and start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Configuration

The `docker-compose.yml` uses environment variables from `.env`:

```yaml
services:
  ax-ploration:
    build: .
    ports:
      - "${API_PORT:-8000}:${API_PORT:-8000}"
    environment:
      - API_HOST=0.0.0.0  # Required for Docker
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
```

### Health Check

The container includes automatic health monitoring:

```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:8000/health
```

## Additional Tools

**Note:** The following directories contain supplementary tools for data preparation and database management. They are not required for running the main application.

### sample-scripts/

Jupyter notebooks demonstrating:
- LangGraph agent workflows
- DataFrame/Graph/Table QA examples
- Agent composition patterns

### db/ and objektartenkatalogExtraction/

Utility scripts for:
- Loading detailed building data into Neo4j
- Extracting building function catalogs
- Database schema inspection and maintenance

These are primarily for data preprocessing and are not needed for regular application use.
