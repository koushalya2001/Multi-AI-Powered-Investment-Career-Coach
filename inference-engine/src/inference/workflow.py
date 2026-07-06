import os
import logging
from google import genai
from google.genai import types
from src.inference.tools import (
    consult_junior_financial_advisor, 
    query_investment_knowledge_base, 
    query_mospi_live, 
    query_insightlaw_live
)

logger = logging.getLogger("Multi_Agent_Workflow")

class MultiAgentSystem:
    def __init__(self):
        # THE ENTERPRISE FIX: Route directly through Vertex AI using GCP IAM
        self.client = genai.Client(
            vertexai=True, 
            project=os.getenv("GOOGLE_CLOUD_PROJECT"), 
            location="us-central1"
        )
        self.model = "gemini-2.5-flash"
        self.chat_history = []

    def run_workflow(self, user_prompt: str) -> str:
        logger.info("--- 🚀 Starting Multi-Agent Inference ---")
        
        # 1. ORCHESTRATOR: Context Management
        self.chat_history.append(f"User: {user_prompt}")
        context_string = "\n".join(self.chat_history[-4:]) 

        # 2. SENIOR STRATEGIST: Tool Execution (A2A, Datastore, MoSPI)
        logger.info("Agent 1: Strategist is pulling data...")
        strategist_prompt = (
            "You are the Senior Investment Strategist. Context:\n" f"{context_string}\n\n"
            "Task: Answer the user's prompt. You MUST use your tools: Use `consult_junior_financial_advisor` for market risk/stock data. "
            "Use `query_investment_knowledge_base` to check our internal documents/videos. Use `query_mospi_live` for macro-economic stats."
        )
        
        strategist_response = self.client.models.generate_content(
            model=self.model,
            contents=strategist_prompt,
            config=types.GenerateContentConfig(
           tools=[
        consult_junior_financial_advisor, 
        query_investment_knowledge_base, 
        query_mospi_live, 
        
        # Advanced Vertex AI Grounding with Dynamic Retrieval
        types.Tool(
            google_search=types.GoogleSearch()
        )
    ],
    # This tells Vertex AI: "Only use Google Search if you are less than 70% confident in your baseline knowledge."
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="AUTO"
        )
    ),
    temperature=0.3
)
        )
        baseline_plan = strategist_response.text

        # 3. ADVERSARIAL CRITIC: Legal Red-Teaming (InsightLaw)
        logger.info("Agent 2: Critic is red-teaming...")
        critic_prompt = (
            "You are the Adversarial Risk Critic. Review this strategy: \n" f"{baseline_plan}\n\n"
            "Use the `query_insightlaw_live` tool to find legal loopholes or compliance risks in India. "
            "Output your critique."
        )
        
        critic_response = self.client.models.generate_content(
            model=self.model,
            contents=critic_prompt,
            config=types.GenerateContentConfig(
                tools=[query_insightlaw_live],
                temperature=0.4
            )
        )
        critique = critic_response.text

        # 4. SYNTHESIZER: Final Output & Resources
        logger.info("Agent 3: Synthesizer formatting output...")
        synth_prompt = (
            "Merge the Baseline Strategy and the Critique into a final response to the user. "
            "If the Strategist provided live news or Google Search facts, explicitly cite the web sources in your '📚 Resources & Data Sources' section"
            "CRITICAL RULE: You must append a section titled '📚 Resources & Data Sources' listing the APIs "
            "and databases used (e.g., Agent Garden, MoSPI, InsightLaw, Vertex Datastore).\n\n"
            f"Strategy:\n{baseline_plan}\n\nCritique:\n{critique}"
        )
        
        final_response = self.client.models.generate_content(
            model=self.model,
            contents=synth_prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        
        self.chat_history.append(f"System: {final_response.text}")
        return final_response.text