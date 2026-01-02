from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic_core import to_jsonable_python

from .schemas import (
    ChatRequest, 
    ChatResponse, 
    HealthResponse, 
    UploadUrlRequest, 
    UploadUrlResponse,
    CreateConversationResponse,
)
from ..database.tables.conversations import BQConversationsTable
from ..database.tables.users import BQUsersTable
from ..database.schemas import (
    ConversationsRequest, 
    UserRecord, 
    AgentRecord, 
    CreateUserRequest, 
    UserResponse, 
    LoginRequest,
)
from ..main import agent 
from ..config import AgentConfig, ModelArmorConfig
from ..security import ModelArmorGuard
from .auxiliars import (
    extract_query_results,
    prepare_to_read_chat_history,
)
from .gcs_utils import generate_upload_url


app = FastAPI(
    title="Lawyer Agent API",
    description="API for the Lawyer Agent",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversations_table = BQConversationsTable()
users_table = BQUsersTable()
agent_config = AgentConfig()
armor_config = ModelArmorConfig()

security_guard = ModelArmorGuard(
    project_id=armor_config.PROJECT_ID,
    location=armor_config.ARMOR_REGION,
    template_id=armor_config.TEMPLATE_ID,
)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status.

    Returns:
        HealthResponse: The status of the service (healthy) and basic info.
    """
    return HealthResponse(
        status="healthy",
        service="Lawyer Agent API",
        description="Agent capable of answering legal questions using BigQuery."
    )


@app.post("/create_user", response_model=UserResponse)
async def create_user(request: CreateUserRequest, response: Response):
    """
    Endpoint to create a new user.

    Args:
        request (CreateUserRequest): The request containing new user details (name, email, hashed_password).

    Returns:
        UserResponse: The result of the creation operation including the new user ID.
    """
    result = users_table.create_user(request)
    if result.status == "error":
        response.status_code = 400
    return result


@app.post("/login", response_model=UserResponse)
async def login(request: LoginRequest, response: Response):
    """
    Endpoint to authenticate an existing user.
    
    Args:
        request (LoginRequest): The request containing email and hashed_password.
        
    Returns:
        UserResponse: The result of the authentication, including user_id if successful.
    """
    result = users_table.authenticate_user(request)
    if result.status == "error":
        response.status_code = 401
    return result


@app.post("/create_conversation_id", response_model=CreateConversationResponse)
async def create_conversation_id():
    """
    Endpoint to generate a new conversation ID.

    Returns:
        CreateConversationResponse: The newly generated conversation ID.
    """
    # Use the conversations table specific ID generation logic to ensure consistency
    conversation_id = conversations_table.generate_conversation_id()
    return CreateConversationResponse(conversation_id=conversation_id)


@app.post("/get_gcs_upload_url", response_model=UploadUrlResponse)
async def get_gcs_upload_url(request: UploadUrlRequest):
    """
    Generates a Signed URL for direct file upload to GCS.

    Args:
        request (UploadUrlRequest): The request containing user_id, conversation_id, and filename.

    Returns:
        UploadUrlResponse: The response containing the generated upload URL and GCS URI.
    """
    BUCKET_NAME = "lawyer_agent"
    # Path structure: user_documents/<user_id>/<conversation_id>/<filename>
    blob_name = f"user_documents/{request.user_id}/{request.conversation_id}/{request.filename}"

    try:
        url = generate_upload_url(
            blob_name=blob_name,
            bucket_name=BUCKET_NAME,
            content_type=request.content_type
        )
        
        return UploadUrlResponse(
            upload_url=url,
            gcs_uri=f"gs://{BUCKET_NAME}/{blob_name}"
        )
    except Exception as e:
        logger.error(f"Error generating signed URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint to interact with the agent.

    Args:
        request (ChatRequest): The chat message and context, including user_id.

    Returns:
        ChatResponse: The agent's response, conversation ID, and executed queries.
    """
    conversation_id = request.conversation_id
    chat_history = []

    # 1. Handle Conversation ID and History
    if conversation_id:
        if conversations_table.conversation_exists(conversation_id):
            logger.info(f"Retrieving history for {conversation_id}")
            chat_history = conversations_table.get_conversation_history(conversation_id)
        else:
            logger.info(f"Conversation {conversation_id} not found. Starting fresh.")

    # Prepare history for the agent
    chat_history_formatted = prepare_to_read_chat_history(chat_history) if chat_history else []

    # 2. Security Check (Input)
    if not security_guard.sanitize_prompt(request.message):
        logger.warning(f"Prompt blocked for {conversation_id}")
        return ChatResponse(
            response="Prompt blocked for security reasons",
            conversation_id=conversation_id if conversation_id else "",
            queries_executed=[],
        )

    try:
        # 3. Run Agent
        logger.info(f"Running agent for conversation ID: {conversation_id}")
        result = await agent.run(request.message, message_history=chat_history_formatted)

        # 4. Extract Results
        queries_executed = extract_query_results(result)
        
        raw_response = result.output
        
        # 5. Security Check (Output)
        safe_response = security_guard.sanitize_response(raw_response)

        # 6. Save to Database
        conv_req = ConversationsRequest(
            conversation_id=conversation_id, # Can be None
            user=UserRecord(
                id=request.user_id,
                prompt=request.message,
            ),
            agent=AgentRecord(
                response=safe_response,
                steps=to_jsonable_python(result.new_messages())
            ),
        )
        
        # add_row handles ID generation if needed
        conversation_id = conversations_table.add_row(conv_req)

        return ChatResponse(
            response=safe_response,
            conversation_id=conversation_id,
            queries_executed=queries_executed,
        )

    except Exception as e:
        logger.error(f"Error in chat execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
