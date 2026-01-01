from pydantic import BaseModel, Field
from typing import Annotated, Optional, List
from ..tools.bigquery.schemas import BigQueryExecution

# Input Schema
class ChatRequest(BaseModel):
    message: Annotated[str, Field(description="The user's message to the agent.")]
    user_id: Annotated[str, Field(description="The unique identifier for the user.")]
    conversation_id: Annotated[Optional[str], Field(description="The unique identifier for the conversation. If not provided, a new one will be generated.")] = None

# Output Schemas
class ChatResponse(BaseModel):
    response: Annotated[str, Field(description="The text response from the agent.")]
    conversation_id: Annotated[str, Field(description="The unique identifier for the conversation.")]
    queries_executed: Annotated[List[BigQueryExecution], Field(description="List of BigQuery queries executed by the agent.")]

class HealthResponse(BaseModel):
    status: Annotated[str, Field(description="The health status of the application.")]
    service: Annotated[str, Field(description="The name of the service.")]
    description: Annotated[str, Field(description="A brief description of the agent.")]
