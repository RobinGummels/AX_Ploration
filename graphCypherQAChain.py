from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence


os.environ["NEO4J_URI"] = "neo4j+s://99128610.databases.neo4j.io"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "HqI-vySN6pQcsWGDANdvYIhuP5SbXMzv2yKPdQK07OU"

graph = Neo4jGraph()

llm = ChatOpenAI(
    model="meta-llama-3.1-8b-instruct",
    temperature=0,
    api_key="ee98985deee87986ae0d135b25a267e8",
    base_url="https://chat-ai.academiccloud.de/v1",
)


schema = """
Database Schema:

Node Labels:
- District(name, centroid, geometry)
- Building(name, centroid, area, floors_above, floors_below, post_code, house_number, uuid)
- Function(code, name)

Relationships:
- (Building)-[:IN_DISTRICT]->(District)
- (Building)-[:HAS_FUNCTION]->(Function)

RULES FOR GENERATING CYPHER:
1. Always put WHERE before RETURN.
2. Always convert numeric string fields using toInteger().
3. Never return entire nodes. Always return selected properties.
4. Never return the centroid or geometry unless explicitly asked.
5. Return only final Cypher. Do not add commentary.
"""

cypher_prompt = ChatPromptTemplate.from_messages([
    ("system", f"You are a Neo4j Cypher expert. Generate only Cypher queries. Do not explain the query. Use this schema:\n{schema}"),
    ("human", "{input}")
])

cypher_llm = RunnableSequence(cypher_prompt, llm)

chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=cypher_llm,
    qa_llm=llm,
    verbose=True,
    allow_dangerous_requests=True
)
question = "Show me all districts."

print(chain.invoke(question))