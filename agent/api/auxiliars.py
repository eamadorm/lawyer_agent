from loguru import logger
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import (
    ToolReturnPart,
    ToolCallPart,
    ModelMessagesTypeAdapter,
    ModelMessage,
)
from pydantic_ai.agent import AgentRunResult
from ..tools.bigquery.schemas import BigQueryExecution
from typing import Union


def _get_tool_parts(
    agent_response: AgentRunResult, matching_tools: list[str]
) -> dict[str, dict[str, Union[ToolCallPart, ToolReturnPart]]]:
    """
    Returns the ToolCallPart and ToolReturnPart of the different tools executed during the last agent run.

    Args:
        agent_response: AgentRunResult -> Object returned by agent.run(prompt)
        matching_tools: list[str] -> List of tool names to look for

    Returns:
        dictionary with two keys:
            "tool_calls" ->  Contains a dictionary where:
                        - keys are the tool_call_ids
                        - values are the ToolCallPart objects

            "tool_returns" -> Contains a dictionary where:
                        - keys are the tool_call_ids
                        - values are the ToolReturnPart
    """
    # This list will contain ToolCallPart and ToolReturnPart objects
    tool_parts = []

    # Looking for the ToolCallPart and ToolReturnPart objects, check documentation: https://ai.pydantic.dev/api/messages/
    for message in agent_response.new_messages():
        message_parts = message.parts
        for message_part in message_parts:
            if (
                isinstance(message_part, Union[ToolCallPart, ToolReturnPart])
                and message_part.tool_name in matching_tools
            ):
                tool_parts.append(message_part)

    # Create maps for easy lookup
    calls_map = {
        part.tool_call_id: part for part in tool_parts if isinstance(part, ToolCallPart)
    }
    returns_map = {
        part.tool_call_id: part
        for part in tool_parts
        if isinstance(part, ToolReturnPart)
    }

    return {"tool_calls": calls_map, "tool_returns": returns_map}


def extract_query_results(agent_response: AgentRunResult) -> list[BigQueryExecution]:
    """
    Extract executed BigQuery queries and their results from an AgentRunResult object.

    Args:
        agent_response (AgentRunResult): The response from the agent containing executed tool calls.

    Returns:
        List[BigQueryExecution]: A list of BigQueryExecution objects containing query IDs, queries, and their results.
    """
    logger.info("Getting query results...")
    tool_parts = _get_tool_parts(
        agent_response,
        matching_tools=[
            "execute_bq_query",
        ],
    )

    tool_calls = tool_parts.get("tool_calls")
    tool_returns = tool_parts.get("tool_returns")

    query_results = list()

    # Gathering SQL queries and its results..."
    for tool_call_id, tool_call_obj in tool_calls.items():
        # Get the response for the query_id
        tool_response_obj = tool_returns.get(tool_call_id)

        if tool_response_obj:
            tool_data = BigQueryExecution(
                query_id=tool_call_id,
                query=tool_call_obj.args.get("query"),
                results=tool_response_obj.content.results,
            )
            query_results.append(tool_data)
        else:
            logger.warning(
                f"Found query call {tool_call_id} but no return value found."
            )

    logger.info(f"Queries found: {len(tool_calls)}")

    return query_results


def extract_plotly_charts(agent_response: AgentRunResult) -> list[dict]:
    """
    Get the 'plotly' dictionaries generated when asking to generate an image. This dictionaries can be easy converted
    into plotly graphs.

    Args:
        agent_response (AgentRunResult): The response from the agent containing executed tool calls.

    Returns:
        list[dict] -> List of dictionaries, each dictionary represents a plotly chart
    """
    logger.info("Getting plotly charts...")
    tool_parts = _get_tool_parts(
        agent_response=agent_response,
        matching_tools=[
            "render_bar_chart",
            "render_histogram",
            "render_box_plot",
            "render_line_chart",
        ],
    )

    tool_calls = tool_parts.get("tool_calls")
    tool_returns = tool_parts.get("tool_returns")

    plotly_charts = list()

    for tool_call_id in tool_calls.keys():
        # Get the response for the query_id
        tool_response_obj = tool_returns.get(tool_call_id)

        if tool_response_obj:
            plotly_dict = tool_response_obj.content.figure

            plotly_charts.append(plotly_dict)

    logger.info(f"Plotly charts found: {len(plotly_charts)}")

    return plotly_charts


def prepare_to_read_chat_history(chat_history: list[dict]) -> list[ModelMessage]:
    """
    Convert a chat session history that is obtained as a list of dictionaries and
    transform it into a list[ModelMessage] that the agent can read during chat sessions.

    Args:
        chat_history: list[dict] -> list of dictionaries obtained fron the database, this contains all the
                                    agent steps, not only the answer/response

    Returns:
        list[ModelMessage] -> List of ModelMessage objects that the agent can process
    """

    # Validates the structure of the python objects
    chat_history = to_jsonable_python(chat_history)

    # Convert into a list of ModelMessage
    chat_history = ModelMessagesTypeAdapter.validate_python(chat_history)

    return chat_history


def extract_echarts_data(agent_response: AgentRunResult) -> list[dict]:
    """
    Extracts ECharts data from tool returns.

    Args:
        agent_response (AgentRunResult): The response from the agent containing executed tool calls.

    Returns:
        list[dict] -> List of dictionaries, each dictionary represents an echarts configuration/data
    """
    logger.info("Getting ECharts data...")
    tool_parts = _get_tool_parts(
        agent_response=agent_response,
        matching_tools=[
            "get_stacked_bar_data",
            "get_pie_data",
            "get_stacked_area_data",
            "get_mix_line_bar_data",
        ],
    )

    tool_calls = tool_parts.get("tool_calls")
    tool_returns = tool_parts.get("tool_returns")

    echarts_data_list = list()

    for tool_call_id in tool_calls.keys():
        # Get the response for the query_id
        tool_response_obj = tool_returns.get(tool_call_id)

        if tool_response_obj:
            # The content of the tool return is the Pydantic model response
            # We want to convert it to a dict to send it via API
            # tool_response_obj.content is the actual return value of the function (the Pydantic model)
            echarts_data = to_jsonable_python(tool_response_obj.content)

            # We assume the frontend needs to know which type of chart it is,
            # but the model response itself (EChartStackedResponse/EChartPieResponse)
            # might be enough if it has a specific structure.
            # However, looking at the models, they don't explicitly say "type": "bar".
            # The tool name might be useful, but `extract_plotly_charts` just returns the content.
            # Let's return the content directly as it matches the "Output Model" requirement.

            # OPTIONAL: Inject the tool name if needed for frontend switching,
            # but usually the structure or a 'type' field in the model is better.
            # For now, we just return the data.
            echarts_data_list.append(echarts_data)

    logger.info(f"ECharts data found: {len(echarts_data_list)}")

    return echarts_data_list
