from .bq_base_table import BigQueryTable
from ..config import DBConfig
from ..schemas import User, UserResponse, CreateUserRequest, UpdatePasswordRequest, DeleteUserRequest, LoginRequest
from ..bq_utils import query_data, insert_rows_from_json
from loguru import logger
from datetime import datetime, timezone
import hashlib

db_config = DBConfig()


class BQUsersTable(BigQueryTable):
    __name: str = db_config.USERS_TABLE_NAME
    __primary_key: str = db_config.USERS_TABLE_PK

    @property
    def name(self) -> str:
        return self.__name

    @property
    def primary_key(self) -> str:
        return self.__primary_key

    def _generate_id(self, email: str) -> str:
        """
        Generates a unique User ID based on the email.
        Format: UID-<hash_of_email>

        Returns:
            str: Generated unique ID.
        """
        # Create SHA256 hash of user email
        sha_hash = hashlib.sha256(email.encode()).hexdigest()
        return f"UID-{sha_hash}"

    def _get_stored_password_hash(self, user_id: str) -> str | None:
        """
        Retrieves the stored password hash for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str | None: The stored hash value, or None if user/field not found.
        """
        query = f"""
            SELECT hashed_password
            FROM `{self.project_id}.{self.dataset_id}.{self.name}`
            WHERE {self.primary_key} = '{user_id}'
        """
        try:
            results = list(query_data(query))
            if not results:
                return None
            return results[0].get("hashed_password")
        except Exception as e:
            logger.error(f"Error fetching password for {user_id}: {e}")
            return None

    def _insert_row(self, user: User) -> None:
        """
        Insert user data into the BigQuery database. Core logic only.

        Args:
            user (User): Class containing the user info.

        Returns:
            None
        """
        logger.info("Inserting user data...")

        try:
            insert_rows_from_json(
                table_name=self.name,
                dataset_name=self.dataset_id,
                project_id=self.project_id,
                rows=[
                    user.model_dump(),
                ],
            )
        except Exception as e:
            logger.error(f"Error while inserting user data into BigQuery: {e}")
            return

    def create_user(self, request: CreateUserRequest) -> UserResponse:
        """
        Creates a new user in the database.

        Args:
            request (CreateUserRequest): The request containing name, email, and hashed_password.

        Returns:
            UserResponse: The response containing the generated user_id and operation status.
        """
        # Note: Validation of password and email uniqueness happens here/pydantic
        # Password passed here is hashed by Pydantic during model instantiation.
        
        email = request.email
        user_id = self._generate_id(email)

        # Check if user already exists
        if self._id_in_table(
            primary_key_row_value=user_id,
            primary_key_column_name=self.primary_key,
            table_name=self.name
        ):
            msg = f"User with email '{email}' already exists."
            logger.error(msg)
            return UserResponse(user_id=user_id, message=msg, status="error")
            
        now = datetime.now(timezone.utc)
        
        # Instantiate User model (hashes password)
        # Use model_construct to avoid double hashing/validation on already hashed password
        try:
            user = User(
                user_id=user_id,
                name=request.name,
                email=request.email,
                hashed_password=request.hashed_password, # Already hashed by CreateUserRequest
                created_at=now,
                updated_at=now
            )
        except ValueError as e:
             return UserResponse(user_id=None, message=str(e), status="error")
        
        self._insert_row(user)
        msg = f"User created successfully with ID: {user_id}"
        logger.info(msg)
        return UserResponse(user_id=user_id, message=msg, status="success")

    def delete_user(self, request: DeleteUserRequest) -> UserResponse:
        """
        Deletes a user from the database after verifying credentials.

        Args:
            request (DeleteUserRequest): Request containing email and password for authentication.

        Returns:
            UserResponse: Status of the deletion operation.
        """
        user_id = self._generate_id(request.email)

        # 1. Check if user exists
        if not self._id_in_table(user_id, self.primary_key, self.name):
            msg = f"User with email {request.email} not found."
            logger.warning(msg)
            return UserResponse(user_id=None, message=msg, status="error")

        # 2. Verify Password
        stored_hash = self._get_stored_password_hash(user_id)
        
        if stored_hash != request.hashed_password:
             msg = "Authentication failed: Password mismatch."
             logger.warning(msg)
             return UserResponse(user_id=user_id, message=msg, status="error")

        # 3. Delete
        query = f"""
            DELETE FROM `{self.project_id}.{self.dataset_id}.{self.name}`
            WHERE {self.primary_key} = '{user_id}'
        """
        
        try:
            list(query_data(query))
            msg = f"User {user_id} deleted successfully."
            logger.info(msg)
            return UserResponse(user_id=user_id, message=msg, status="success")
        except Exception as e:
            msg = f"Error deleting user {user_id}: {e}"
            logger.error(msg)
            return UserResponse(user_id=user_id, message=msg, status="error")

    def update_password(self, request: UpdatePasswordRequest) -> UserResponse:
        """
        Updates a user's password after verifying current credentials.
        
        Args:
            request (UpdatePasswordRequest): Request containing email, current_hashed_password, and new_hashed_password.

        Returns:
            UserResponse: Status of the update operation.
        """
        user_id = self._generate_id(request.email)
        
        # 1. Check existence
        if not self._id_in_table(user_id, self.primary_key, self.name):
            msg = f"User with email {request.email} not found."
            logger.error(msg)
            return UserResponse(user_id=None, message=msg, status="error")

        # 2. Check stored hash matches provided current password
        stored_hash = self._get_stored_password_hash(user_id)
        
        # request.current_hashed_password is actually the HASH of the input string due to HASH_PASSWORD_FIELD validator
        if stored_hash != request.current_hashed_password:
             msg = "Authentication failed: Incorrect current password."
             logger.warning(msg)
             # Returning successful=False
             return UserResponse(user_id=user_id, message=msg, status="error")

        # 3. Check idempotent (New == Old)
        if stored_hash == request.new_hashed_password:
             msg = "New password matches the current one. No changes made."
             logger.info(f"User {user_id}: Password update skipped (identical).")
             return UserResponse(user_id=user_id, message=msg, status="success")

        # 4. Update
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = request.new_hashed_password
        
        query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.{self.name}`
            SET hashed_password = '{new_hash}', updated_at = '{now_str}'
            WHERE {self.primary_key} = '{user_id}'
        """

        try:
            list(query_data(query))
            msg = "User password updated successfully."
            logger.info(msg)
            return UserResponse(user_id=user_id, message=msg, status="success")
        except Exception as e:
            msg = f"Error updating user {user_id}: {e}"
            logger.error(msg)
            return UserResponse(user_id=user_id, message=msg, status="error")

    def authenticate_user(self, request: LoginRequest) -> UserResponse:
        """
        Authenticates a user by verifying credentials.

        Args:
            request (LoginRequest): Request containing email and hashed_password.

        Returns:
            UserResponse: The response containing the user_id if successful, or error status.
        """
        user_id = self._generate_id(request.email)

        # 1. Check existence
        if not self._id_in_table(user_id, self.primary_key, self.name):
            msg = f"Authentication failed: User with email {request.email} not found."
            logger.warning(msg)
            return UserResponse(user_id=None, message=msg, status="error")

        # 2. Verify Password
        stored_hash = self._get_stored_password_hash(user_id)

        if stored_hash != request.hashed_password:
             msg = "Authentication failed: Incorrect password."
             logger.warning(msg)
             return UserResponse(user_id=None, message=msg, status="error")

        msg = "User authenticated successfully."
        logger.info(f"User {user_id} logged in.")
        return UserResponse(user_id=user_id, message=msg, status="success")
