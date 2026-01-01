from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime
from pydantic.functional_serializers import PlainSerializer


class ConversationsRequest(BaseModel):
    conversation_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="ID of the conversation",
        ),
    ]
    prompt_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Unique ID of the prompt",
        ),
    ]
    user_prompt: Annotated[
        str,
        Field(
            description="User Prompt",
        ),
    ]
    agent_response: Annotated[
        str,
        Field(
            description="Agent's answer",
        ),
    ]
    agent_response_steps: Annotated[
        list[dict],
        Field(
            description="Agent's internal steps",
        ),
    ]
    prompt_created_at: Annotated[
        datetime,
        Field(
            default=None,
            description="Datetime when a resource was created",
        ),
        PlainSerializer(  # Tells pydantic when serializing (converting to a dict or a json string), use the function
            lambda dt: dt.strftime(r"%Y-%m-%d %H:%M:%S"),
            when_used="always",
        ),
    ]
