"""
FastAPI Server for AX_Ploration Agent with Streaming Support

Start the server:
    python -m backend.api.server
    
Or with uvicorn directly:
    uvicorn backend.api.server:app --reload --host localhost --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncIterator
import json
import sys
import asyncio
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from scripts.config import validate_config, API_PORT, API_HOST
from scripts.graph import graph
from scripts.main import create_initial_state
from scripts.utils.neo4j_client import neo4j_client


app = FastAPI(
    title="AX_Ploration API",
    description="API for querying Berlin building data using natural language",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str
    stream: Optional[bool] = True
    spatial_filter: Optional[str] = None  # WKT geometry string in EPSG:25833


class QueryResponse(BaseModel):
    """Response model for non-streaming queries."""
    query: str
    final_answer: str
    query_type: Optional[str] = None
    building_functions: Optional[list] = None
    building_function_names: Optional[list] = None
    results_count: Optional[int] = None
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Validate configuration and database connection on startup."""
    try:
        validate_config()
        if not neo4j_client.verify_connection():
            raise RuntimeError("Could not connect to Neo4j database")
        print("Server started successfully")
        print("Neo4j connection verified")
    except Exception as e:
        print(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    neo4j_client.close()
    print("Server shutdown complete")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AX_Ploration API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check including database connection."""
    db_status = neo4j_client.verify_connection()
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected"
    }


async def stream_agent_state(query: str, spatial_filter: str = None) -> AsyncIterator[str]:
    """
    Stream agent execution messages as Server-Sent Events.
    
    Yields JSON objects with:
    - type: "message" - incremental messages during execution
    - content: the message text
    
    - type: "final" - complete final state when done
    - state: the full AgentState as JSON
    
    - type: "error" - error occurred
    - error: error message
    """
    try:
        initial_state = create_initial_state(query, spatial_filter)
        sent_messages = set()  # Track which messages we've already sent
        
        # Stream graph execution with stream_mode="values" to get complete state each time
        final_state = None
        for step_output in graph.stream(initial_state, stream_mode="values"):
            # step_output is now the complete state after each node
            # Get all current messages
            all_messages = step_output.get("messages", [])
            
            # Send only new messages we haven't sent yet
            for i, message in enumerate(all_messages):
                message_id = f"{i}:{message}"  # Create unique ID
                if message_id not in sent_messages:
                    yield f"data: {json.dumps({'type': 'message', 'content': message}, ensure_ascii=False)}\n\n"
                    sent_messages.add(message_id)
                    await asyncio.sleep(0)
            
            final_state = step_output
        
        # Send final complete state - convert TypedDict to regular dict for JSON serialization
        if final_state:
            # Create a complete copy with all fields from AgentState
            complete_state = {
                "query": final_state.get("query", ""),
                "attributes": final_state.get("attributes", []),
                "needs_building_function": final_state.get("needs_building_function", False),
                "building_functions": final_state.get("building_functions", []),
                "building_function_names": final_state.get("building_function_names", []),
                "building_function_descriptions": final_state.get("building_function_descriptions", []),
                "query_type": final_state.get("query_type", ""),
                "cypher_query": final_state.get("cypher_query", ""),
                "results": final_state.get("results", []),
                "spatial_comparison": final_state.get("spatial_comparison"),
                "final_answer": final_state.get("final_answer", ""),
                "error": final_state.get("error"),
                "messages": final_state.get("messages", [])
            }
            yield f"data: {json.dumps({'type': 'final', 'state': complete_state}, ensure_ascii=False, default=str)}\n\n"
        
    except Exception as e:
        error_msg = f"Error during agent execution: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'error': error_msg}, ensure_ascii=False)}\n\n"


@app.post("/query")
async def query_agent(request: QueryRequest):
    """
    Process a natural language query about Berlin buildings.
    
    Args:
        request: QueryRequest with query string and optional stream flag
        
    Returns:
        StreamingResponse with Server-Sent Events (if stream=True)
        or QueryResponse with final result (if stream=False)
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Streaming response
    if request.stream:
        return StreamingResponse(
            stream_agent_state(request.query, request.spatial_filter),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
    # Non-streaming response
    try:
        initial_state = create_initial_state(request.query, request.spatial_filter)
        final_state = graph.invoke(initial_state)
        
        # Return complete AgentState as JSON
        return final_state
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/functions")
async def list_building_functions():
    """List all available building functions from the database."""
    try:
        functions = neo4j_client.get_building_functions()
        return {
            "count": len(functions),
            "functions": functions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching functions: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print(f"Starting AX_Ploration API on Port: {API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
