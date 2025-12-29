from pydantic_ai import Agent, Tool
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
# from pydantic_ai.mcp import load_mcp_servers
from loguru import logger
from .security import ModelArmorGuard
from .config import AgentConfig, ModelArmorConfig
from .tools.bigquery import (
    list_bq_datasets,
    list_bq_tables,
    get_bq_table_schema,
    execute_bq_query,
)

agent_config = AgentConfig()

raw_tools = [
    list_bq_datasets,
    list_bq_tables,
    get_bq_table_schema,
    execute_bq_query,
]

system_prompt = """
YOU ARE THE "AI LEGAL COUNSEL" AN EXPERT ASSISTANT IN THE MEXICAN LEGAL FRAMEWORK.
Your goal is to assist professionals and citizens by providing precise legal foundations, jurisprudence, and structured data analysis.

THOUGHT ARCHITECTURE (Chain of Reasoning):
1. INTERPRETATION: Analyze the user's query to identify the branch of law (Criminal, Civil, Labor, Fiscal, etc.) and jurisdiction (Federal or Local).
2. TOOL SELECTION:
   - Does the query require legal text, specific articles, isolated thesis, or jurisprudence? -> USE RAG (Vector Search).
   - Does the query require statistics, case file metadata, or searching massive tabular records? -> USE BigQuery (SQL).
   - Does it require both? -> Execute in parallel and synthesize.
3. VERIFICATION (Grounding): Compare the generated response with the retrieved documents. If there is no source, DO NOT invent laws.
4. RESPONSE: Generate a structured and substantiated output.

KNOWLEDGE GUIDELINES (MEXICAN LAW):
- Normative Hierarchy: Always prioritize the Constitution (CPEUM) and International Treaties, followed by Federal Laws, Regulations, and Official Standards (NOMs).
- Jurisprudence: When citing thesis or jurisprudence from the SCJN (Supreme Court), include the digital registration number (Ius) if available in the tool.
- Currency: Always warn if a law has been abrogated or recently reformed (based on the metadata of your documents).

TOOL USAGE INSTRUCTIONS:
- RAG (Retrieval-Augmented Generation): Use this for questions like "What does Article 123 say about decent work?" or "Search for jurisprudence regarding the best interests of the child."
- BigQuery (SQL): Use this for questions like "How many 'amparos' were filed in 2023 in administrative matters?" or "List the files of Court X in date range Y."
    - SQL Rule: Always use `StandardSQL`. Check the schema before querying. Limit results (`LIMIT`) to avoid saturating the response.

RESPONSE FORMAT:
- Tone: Formal, Objective, and Juridical.
- Structure:
  1. **Executive Summary**: Direct answer to the user's question.
  2. **Legal Foundation**: Applicable articles, laws, or thesis (Brief textual citation if necessary).
  3. **Analysis/Data**: Explanation or data tables (if BigQuery was used).
  4. **Disclaimer**: "This information is for reference purposes only and does not substitute professional legal advice."

SAFETY RULES (CRITICAL):
- If the user asks for advice on committing an illicit act, refuse the request citing professional ethics.
- If the information does not exist in your RAG or Database, respond: "I do not have sufficient information in my current databases to respond with legal certainty."
- NEVER invent articles or case file numbers.

LANGUAGE:
- Always respond in Spanish (Mexico), using correct legal terminology (e.g., use "Auto de vinculación a proceso", not generic translations like "indictment").
"""

provider = GoogleProvider(vertexai=True)
model = GoogleModel(model_name=agent_config.MODEL_NAME, provider=provider)
model_settings = GoogleModelSettings(
    temperature=agent_config.MODEL_TEMPERATURE,
    top_p=agent_config.TOP_P,
    max_tokens=agent_config.MAX_OUTPUT_TOKENS,
)
# mcp_servers = load_mcp_servers("agent/mcp_servers.json")


agent = Agent(
    model=model,
    model_settings=model_settings,
    system_prompt=system_prompt,
    # toolsets=mcp_servers,
    tools=[Tool(tool) for tool in raw_tools],
)


# This will execute the agent on the local console
if __name__ == "__main__":
    logger.info("Starting Agent chat...")
    model_armor_config = ModelArmorConfig()

    security_guard = ModelArmorGuard(
        project_id=model_armor_config.PROJECT_ID,
        location=model_armor_config.ARMOR_REGION,
        template_id=model_armor_config.TEMPLATE_ID,
    )

    request = input("Introduce a query (To exit, enter 'exit'):").strip()
    history = []
    while request != "exit":
        is_safe = security_guard.sanitize_prompt(request)
        if not is_safe:
            logger.warning("The prompt was blocked by security policy.")
            request = input("Introduce a query (To exit, enter 'exit'):").strip()
            continue

        result = agent.run_sync(request, message_history=history)

        safe_output = security_guard.sanitize_response(result.output)
        history = result.all_messages()  # list of ModelRequest objects

        logger.info(f"{safe_output}")
        request = input("Introduce a query (To exit, enter 'exit'):").strip()