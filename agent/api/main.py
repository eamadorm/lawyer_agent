import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic_core import to_jsonable_python
from typing import List, Optional, Dict, Any

from .schemas import ChatRequest, ChatResponse, HealthResponse
from ..database.tables.conversations import BQConversationsTable
from ..database.schemas import ConversationsRequest
from ..main import agent 
from ..config import AgentConfig, ModelArmorConfig
from ..security import ModelArmorGuard
from .auxiliars import (
    extract_query_results,
    prepare_to_read_chat_history,
)

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
agent_config = AgentConfig()
armor_config = ModelArmorConfig()

security_guard = ModelArmorGuard(
    project_id=armor_config.PROJECT_ID,
    location=armor_config.ARMOR_REGION,
    template_id=armor_config.TEMPLATE_ID,
)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Lawyer Agent API",
        description="Agent capable of answering legal questions using BigQuery."
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint to interact with the agent.
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
            user_prompt=request.message,
            agent_response=safe_response,
            agent_response_steps=to_jsonable_python(result.new_messages())
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
