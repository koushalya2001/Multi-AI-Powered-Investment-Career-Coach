import os
import uuid
import logging
import requests
from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud.dialogflowcx_v3 import SessionsClient, TextInput, QueryInput, DetectIntentRequest

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
# TOOL 3: Live MoSPI Data
# ==========================================
def query_mospi_live(indicator_query: str) -> str:
    """Queries the live Indian Ministry of Statistics Data Innovation API for economic metrics."""
    try:
        # Hitting the public innovation layer API
        url = "https://datainnovation.mospi.gov.in/api/v1/search"
        response = requests.get(url, params={"q": indicator_query}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return str(data.get("results", "No data found for this indicator."))[:1000] # Cap length
        return "MoSPI API returned non-200 status."
    except Exception as e:
        return f"MoSPI API Error: {e}"

# ==========================================
# TOOL 4: Live InsightLaw
# ==========================================
def query_insightlaw_live(legal_query: str) -> str:
    """Queries the live InsightLaw API for Indian legal sections and corporate compliance."""
    try:
        url = "https://insightlaw.in/api/search"
        response = requests.get(url, params={"q": legal_query}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return str(data.get("data", "No legal statutes found."))[:1000]
        return "InsightLaw API returned non-200 status."
    except Exception as e:
        return f"InsightLaw API Error: {e}"