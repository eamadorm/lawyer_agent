from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import DocumentUrl
from typing import Annotated, Optional, List
from ..tools.bigquery.schemas import BigQueryExecution


class UploadUrlRequest(BaseModel):
    filename: Annotated[str, Field(description="The name of the file to upload.")]
    content_type: Annotated[str, Field(description="The MIME type of the file.")]
    user_id: Annotated[str, Field(description="The ID of the user uploading the file.")]
    conversation_id: Annotated[str, Field(description="The ID of the conversation.")]

class ChatRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    message: Annotated[str, Field(description="The user's message to the agent.")]
    user_id: Annotated[str, Field(description="The unique identifier for the user.")]
    conversation_id: Annotated[Optional[str], Field(description="The unique identifier for the conversation. If not provided, a new one will be generated.")] = None
    documents: Annotated[List[DocumentUrl], Field(default = list(), description="List of documents associated with the message.")]


class UploadUrlResponse(BaseModel):
    upload_url: Annotated[str, Field(description="The signed URL for direct upload.")]
    gcs_uri: Annotated[str, Field(description="The final GCS URI of the uploaded file.")]

class CreateConversationResponse(BaseModel):
    conversation_id: Annotated[str, Field(description="The unique identifier for the new conversation.")]

class ChatResponse(BaseModel):
    response: Annotated[str, Field(description="The text response from the agent.")]
    conversation_id: Annotated[str, Field(description="The unique identifier for the conversation.")]
    queries_executed: Annotated[List[BigQueryExecution], Field(description="List of BigQuery queries executed by the agent.")]

class HealthResponse(BaseModel):
    status: Annotated[str, Field(description="The health status of the application.")]
    service: Annotated[str, Field(description="The name of the service.")]
    description: Annotated[str, Field(description="A brief description of the agent.")]
