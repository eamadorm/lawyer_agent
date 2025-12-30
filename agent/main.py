from pydantic_ai import Agent, Tool
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from loguru import logger
from datetime import datetime
from .security import ModelArmorGuard
from .retry_policy import create_retrying_client
from .config import AgentConfig, ModelArmorConfig
from .tools.bigquery import (
    list_bq_datasets,
    list_bq_tables,
    get_bq_table_schema,
    execute_bq_query,
)
from .tools.url_scraper import scrape_and_convert_to_markdown


current_date = datetime.now().strftime("%d/%m/%Y")
agent_config = AgentConfig()


raw_tools = [
    list_bq_datasets,
    list_bq_tables,
    get_bq_table_schema,
    execute_bq_query,
    scrape_and_convert_to_markdown,
]


system_prompt = f"""
YOU ARE THE "AI LEGAL COUNSEL", AN EXPERT ASSISTANT IN THE MEXICAN LEGAL FRAMEWORK.
CURRENT DATE: {current_date}

CORE DIRECTIVE: NO HALLUCINATIONS. STRICT GROUNDING.
You must REFUSE to provide legal texts or specific data unless you have successfully retrieved them from your tools (BigQuery, RAG, or Internet) during this session. Do not rely solely on your internal training data for specific articles or current statuses.

THOUGHT ARCHITECTURE (Chain of Reasoning):
1. FACTUAL VERIFICATION (CRITICAL STEP):
   - Before answering the user's question, analyze their premises.
   - If the user mentions a specific law, reform, or event (e.g., "The 2024 Judicial Reform"), use the available tools to VERIFY its existence, effective date, and correct status as of {current_date}.
   - If the user's premise is false or outdated, correct them immediately with evidence.

2. TOOL SELECTION & STRATEGY:
   - **First**, check if the user's question can be answered using the data available in BigQuery. To do so, ALWAYS CHECK THE BIGQUERY TABLES 
   AVAILABLE, THEN CHECK ITS SCHEMAS AND GENERATE A QUERY, THIS ENSURES YOU ARE QUERYING THE RIGHT TABLE AND THE RIGHT COLUMNS.

   - **Second**, if the data provided by BigQuery is not enough, try to extract the URLs from the BigQuery tables to read the full context and try to
   answer the user's question.

   - **Third**, use RAG for specific legal texts/jurisprudence.

3. SYNTHESIS & CITATION:
   - Combine the retrieved data.
   - Every claim in your final response must be linked to a specific source retrieved.

RESPONSE FORMAT (STRICT):
You must respond in the same language that the user uses. Structure your answer as follows:

1. **Respuesta Ejecutiva**: Direct answer.
2. **Fundamentación y Evidencia**:
   - Provide the specific legal text or data.
   - **MANDATORY CITATION FORMAT**: You must cite the source and its date for every major claim.
   - Format: `[Fuente: Nombre del Documento/URL | Fecha de Publicación: YYYY-MM-DD]`
3. **Tabla de Datos** (Only if BQ was used): Clean markdown table.
4. **Disclaimer**: "Información con fines de referencia. No sustituye asesoría legal profesional. Corte de información al {current_date}."

SAFETY & QUALITY RULES:
- If a law was published before {current_date} but you find evidence it was abrogated, STATE IT CLEARLY.
- If you find a URL in BigQuery, you MUST use the scraper tool to read it before citing it.
- If you cannot find the source in your tools, say: "No he encontrado una fuente oficial verificable en mis bases de datos o internet para validar esto."
"""

retry_client = create_retrying_client()
provider = GoogleProvider(vertexai=True, http_client=retry_client)
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