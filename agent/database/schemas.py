from pydantic import BaseModel, Field, field_validator, BeforeValidator, AfterValidator
import hashlib
import re
from typing import Annotated, Optional, Literal
from datetime import datetime
from pydantic.functional_serializers import PlainSerializer


## Common Validators
STRING_NORMALIZER = BeforeValidator(
    lambda text: str(text).strip() if text is not None else None
)


# Password Validator Logic
def validate_and_hash_password(v: str) -> str:
    """
    Validates password complexity and hashes it using SHA256.
    Reusable validator for Pydantic models.
    """
    if not v:
        return v

    # Validate complexity using Python's re engine
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[ !#$%^&*(),.?\":{}|<>]).{8,}$"
    if not re.match(pattern, v):
            raise ValueError(
            "Password must contain at least 8 characters, one uppercase, one lowercase, one number and one special character"
        )
    
    # Return the hash
    return hashlib.sha256(v.encode()).hexdigest()

HASH_PASSWORD_FIELD = Annotated[
    str,
    Field(description="Password field that validates complexity and hashes the value"),
    AfterValidator(validate_and_hash_password)
]

USER_NAME_FIELD = Annotated[
    str,
    Field(description="Name of the user"),
    STRING_NORMALIZER,
]

USER_EMAIL_FIELD = Annotated[
    str,
    Field(description="Email of the user"),
    STRING_NORMALIZER,
]


class UserRecord(BaseModel):
    """
    Represents the User record within a conversation.
    """
    id: Annotated[
        str,
        Field(description="User ID"),
        STRING_NORMALIZER,
    ]
    prompt: Annotated[
        str,
        Field(description="User Prompt"),
        STRING_NORMALIZER,
    ]


class AgentRecord(BaseModel):
    """
    Represents the Agent record within a conversation.
    """
    response: Annotated[
        str,
        Field(description="Agent's answer"),
        STRING_NORMALIZER,
    ]
    steps: Annotated[
        list[dict],
        Field(description="Agent's internal steps"),
    ]


class UserResponse(BaseModel):
    """
    Standard response model for user operations.
    """
    user_id: Annotated[
        Optional[str],
        Field(description="ID of the user"),
    ]
    message: Annotated[
        str,
        Field(description="Result message"),
    ]
    status: Annotated[
        Literal["success", "error"],
        Field(description="Status of the operation (success/error)"),
    ]


class CreateUserRequest(BaseModel):
    """
    Request model for creating a new user.
    """
    name: USER_NAME_FIELD
    email: USER_EMAIL_FIELD
    hashed_password: HASH_PASSWORD_FIELD


class LoginRequest(BaseModel):
    """
    Request model for user login.
    """
    email: USER_EMAIL_FIELD
    hashed_password: HASH_PASSWORD_FIELD


class UpdatePasswordRequest(BaseModel):
    """
    Request model for updating an existing user's password.
    """
    email: USER_EMAIL_FIELD
    current_hashed_password: HASH_PASSWORD_FIELD
    new_hashed_password: HASH_PASSWORD_FIELD


class DeleteUserRequest(BaseModel):
    """
    Request model for deleting a user.
    """
    email: USER_EMAIL_FIELD
    hashed_password: HASH_PASSWORD_FIELD  # Using same validator ensures we produce the same hash for verification


class ConversationsRequest(BaseModel):
    """
    Request model for logging a conversation interaction.
    """
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
        )
    ]
    user: Annotated[
        UserRecord,
        Field(description="User interaction record"),
    ]
    agent: Annotated[
        AgentRecord,
        Field(description="Agent response record"),
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


class User(BaseModel):
    """
    Database model representing a User in the users table.
    """
    user_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Unique ID of the user",
        ),
        STRING_NORMALIZER
    ]
    name: USER_NAME_FIELD
    email: USER_EMAIL_FIELD
    hashed_password: Annotated[
        # Due to Pydantic's validation in CreateUserRequest class, this field will always be a hashed password
        str,
        Field(description="Hashed password of the user"),
        STRING_NORMALIZER,
    ]
    created_at: Annotated[
        datetime,
        Field(
            default=None,
            description="Datetime when the user was created",
        ),
        PlainSerializer(
            lambda dt: dt.strftime(r"%Y-%m-%d %H:%M:%S"),
            when_used="always",
        ),
    ]
    updated_at: Annotated[
        datetime,
        Field(
            default=None,
            description="Datetime when the user was last updated",
        ),
        PlainSerializer(
            lambda dt: dt.strftime(r"%Y-%m-%d %H:%M:%S"),
            when_used="always",
        ),
    ]
