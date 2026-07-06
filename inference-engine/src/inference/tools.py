import os
import uuid
import logging
import requests
from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud.dialogflowcx_v3 import SessionsClient, TextInput, QueryInput, DetectIntentRequest
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


logger = logging.getLogger("Live_Tools")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# ==========================================
# TOOL 1: A2A Bridge (Agent Garden Junior Advisor)
# ==========================================
def consult_junior_financial_advisor(query: str) -> str:
    """Sends a query to the deployed Agent Garden Financial Advisor to calculate market risk and fetch stock data."""
    # Add these to your .env or Cloud Run variables!
    agent_id = os.getenv("FINANCIAL_AGENT_ID") 
    location = os.getenv("FINANCIAL_AGENT_LOCATION", "global")
    session_id = str(uuid.uuid4()) # Unique session per query

    if not agent_id:
        return "A2A Error: FINANCIAL_AGENT_ID not set."

    try:
        client_options = {"api_endpoint": f"{location}-dialogflow.googleapis.com"} if location != "global" else None
        client = SessionsClient(client_options=client_options)
        
        session_path = f"projects/{PROJECT_ID}/locations/{location}/agents/{agent_id}/sessions/{session_id}"
        
        request = DetectIntentRequest(
            session=session_path,
            query_input=QueryInput(text=TextInput(text=query), language_code="en")
        )
        
        response = client.detect_intent(request=request)
        if response.query_result.response_messages:
            return " ".join([msg.text.text[0] for msg in response.query_result.response_messages if msg.text])
        return "Junior Advisor returned no analysis."
    except Exception as e:
        logger.error(f"A2A Call Failed: {e}")
        return f"A2A Error: {e}"

# ==========================================
# TOOL 2: Vertex Knowledge Graph (The Datastore)
# ==========================================
def query_investment_knowledge_base(query: str) -> str:
    """Searches the corporate AI Platform Datastore (YouTube videos, PDFs) for domain facts."""
    datastore_id = os.getenv("VERTEX_DATASTORE_ID")
    if not datastore_id:
        return "Datastore disabled."
        
    try:
        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=PROJECT_ID, location="global", data_store=datastore_id, serving_config="default_config"
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config, query=query, page_size=3,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(return_snippet=True)
            )
        )
        response = client.search(request)
        snippets = [s.get("snippet", "") for r in response.results if r.document.derived_struct_data for s in r.document.derived_struct_data.get("snippets", [])]
        return "### Retrieved Context:\n" + "\n".join(snippets) if snippets else "No context found."
    except Exception as e:
        return f"Datastore Error: {e}"

# ==========================================
# TOOL 3: MoSPI MCP Integration (Async wrapped for Sync execution)
# ==========================================
MOSPI_MCP_URL = "https://datainnovation.mospi.gov.in/mospi-mcp"
MOSPI_STATIC_FALLBACK = "Indicative data (live MoSPI MCP unavailable): India CPI inflation ~4.9% YoY, IIP growth ~5.2% YoY, PLFS unemployment rate ~3.2%."

async def _async_mospi_call(query: str) -> str:
    """Internal async handler for the official MoSPI MCP server."""
    try:
        async with streamablehttp_client(MOSPI_MCP_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Assuming the MCP server exposes a 'search_indicators' tool based on NSO repo
                result = await session.call_tool("search_indicators", {"query": query})
                text = "\n".join(c.text for c in result.content if c.type == "text")
                return text[:1500] if text else MOSPI_STATIC_FALLBACK
    except Exception as e:
        logger.error(f"MoSPI MCP Error: {e}")
        return MOSPI_STATIC_FALLBACK

def query_mospi_live(indicator_query: str) -> str:
    """
    Queries the official Indian Ministry of Statistics (MoSPI) MCP server for live macro-economic data.
    Use this for CPI, IIP, PLFS, or general economic statistics.
    """
    # Run the async MCP call safely inside our synchronous app
    return asyncio.run(_async_mospi_call(indicator_query))

# ==========================================
# TOOLS 4-7: InsightLaw Explicit Corpora
# ==========================================
BASE_URL = "https://insightlaw.in/api"
INSIGHTLAW_STATIC_FALLBACK = "Indicative reference (live InsightLaw unavailable): verify against official Gazette text."

def _safe_get(url: str, params: dict = None) -> dict | None:
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.error(f"InsightLaw API Error: {e}")
    return None

def get_constitution_article(article_number: str) -> str:
    """Fetches the exact text of a named article of the Indian Constitution by its number (e.g. '21', '14')."""
    data = _safe_get(f"{BASE_URL}/constitution/article/{article_number}")
    return str(data)[:1000] if data else INSIGHTLAW_STATIC_FALLBACK

def get_bns_section(section_number: str) -> str:
    """Fetches the exact text of a section from the Bharatiya Nyaya Sanhita 2023 (BNS), India's current criminal code."""
    data = _safe_get(f"{BASE_URL}/bns/section/{section_number}")
    return str(data)[:1000] if data else INSIGHTLAW_STATIC_FALLBACK

def get_ipc_section(section_number: str) -> str:
    """Fetches text from the repealed Indian Penal Code (IPC). Use ONLY for historical/legacy references."""
    data = _safe_get(f"{BASE_URL}/ipc/section/{section_number}")
    if data:
        return str(data)[:900] + " [Note: IPC repealed July 2024, replaced by BNS 2023.]"
    return INSIGHTLAW_STATIC_FALLBACK

def query_insightlaw_search(legal_query: str) -> str:
    """Cross-corpus keyword search across Constitution, IPC, and BNS for broad corporate or compliance topics."""
    data = _safe_get(f"{BASE_URL}/search", params={"q": legal_query})
    if data:
        result = data.get("results") or data.get("data")
        if result:
            return str(result)[:1000]
    return INSIGHTLAW_STATIC_FALLBACK