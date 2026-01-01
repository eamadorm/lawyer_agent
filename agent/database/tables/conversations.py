from .bq_base_table import BigQueryTable
from ..config import DBConfig
from ..schemas import ConversationsRequest
from ..bq_utils import query_data, insert_rows_from_json
from loguru import logger
from datetime import datetime, timezone
import secrets
import hashlib

db_config = DBConfig()


class BQConversationsTable(BigQueryTable):
    __name: str = db_config.CONVERSATIONS_TABLE_NAME
    __primary_key: str = db_config.CONVERSATIONS_TABLE_PK

    @property
    def name(self) -> str:
        return self.__name

    @property
    def primary_key(self) -> str:
        return self.__primary_key

    def _generate_id(self) -> str:
        """
        Generates a unique Conversation ID.
        Format: CONV-<20_char_hash>

        Returns:
            str: Generated unique ID.
        """
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%d%H%M%S%f")
        random_salt = secrets.token_hex(4)
        data = f"{timestamp}{random_salt}".encode()

        # Create SHA256 hash
        sha_hash = hashlib.sha256(data).hexdigest()

        # Take first 20 chars to ensure collision resistance for millions of users
        short_hash = sha_hash[:20]

        return short_hash

    def _generate_prompt_id(self, conversation_id: str) -> str:
        """
        Generates a new prompt id (Stateful/Incremental).
        Format: <conversation_id>-00000001

        Args:
            conversation_id (str): The conversation ID.

        Returns:
            str: Generated prompt ID.
        """
        query = f"""
                select
                    max(prompt_id) as max_prompt_id
                from `{self.project_id}.{self.dataset_id}.{self.name}`
                where conversation_id = '{conversation_id}'
                """

        row_iterator = query_data(query=query)
        max_id_row = next(row_iterator, None)

        if not max_id_row or not max_id_row.max_prompt_id:
            next_prompt_id = 1
        else:
            next_prompt_id = int(max_id_row.max_prompt_id[-8:]) + 1

        return f"{conversation_id}P{next_prompt_id:08d}"

    def _insert_row(self, request: ConversationsRequest) -> None:
        """
        Insert conversations data into the BigQuery database. Core logic only.

        Args:
            request (ConversationsRequest): Class containing the conversation info.

        Returns:
            None
        """
        logger.info("Inserting data...")

        try:
            insert_rows_from_json(
                table_name=self.name,
                dataset_name=self.dataset_id,
                project_id=self.project_id,
                rows=[
                    request.model_dump(),
                ],
            )
        except Exception as e:
            raise ValueError(
                f"Error while inserting chat session's data into BigQuery: {e}"
            )

    def add_row(self, request: ConversationsRequest) -> str:
        """
        Checks if the request already contains a conversation id.
        If provided: checks if exists. If not exists -> generates new.
        If not provided: generates new.
        Then generates incremental prompt_id.
        Finally inserts the data.

        Args:
            request (ConversationsRequest): Info related to the conversation.

        Returns:
            str: Id of the conversation.
        """
        logger.debug(
            f"Searching for conversation_id {request.conversation_id} in table {self.name}..."
        )
        # Generating a conversation_id if not provided or not in table
        if not request.conversation_id or not self.conversation_exists(
            request.conversation_id
        ):
            logger.debug(
                f"Conversation_id {request.conversation_id} not found. Generating new one."
            )
            request.conversation_id = self._generate_id()

        logger.debug(
            f"Generating prompt_id for conversation_id {request.conversation_id}..."
        )
        request.prompt_id = self._generate_prompt_id(request.conversation_id)

        logger.debug(f"Adding row to the {self.name} table...")
        request.prompt_created_at = datetime.now(timezone.utc)
        self._insert_row(request)

        return request.conversation_id

    def conversation_exists(self, conversation_id: str) -> bool:
        """
        Checks if a conversation exists in the BigQuery table.

        Args:
            conversation_id (str): The ID of the conversation to check.

        Returns:
            bool: True if the conversation exists, False otherwise.
        """
        return self._id_in_table(
            primary_key_row_value=conversation_id,
            primary_key_column_name="conversation_id",
            table_name=self.name,
        )

    def get_conversation_history(self, conversation_id: str) -> list[dict]:
        """
        Retrieves the whole conversation history of a conversation_id.

        Args:
            conversation_id (str): Id of the conversation.

        Returns:
             list[dict]: List of conversation steps.
        """
        if not self.conversation_exists(conversation_id):
            logger.error(
                f"The ID {conversation_id} does not exists in BQ table {self.name}"
            )
            return

        query = f"""
                select
                
                array_agg(steps ORDER BY prompt_created_at ASC) as full_history

                FROM `{self.project_id}.{self.dataset_id}.{self.name}`,
                UNNEST(agent.steps) steps
                WHERE conversation_id = '{conversation_id}'

                GROUP BY conversation_id
                """

        row_iterator = query_data(query=query)

        full_history = next(row_iterator).full_history

        return full_history
