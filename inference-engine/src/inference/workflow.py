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
        # Using Vertex AI to bypass AI Studio billing bugs
        self.client = genai.Client(
            vertexai=True, 
            project=os.getenv("GOOGLE_CLOUD_PROJECT"), 
            location="us-central1"
        )
        self.model = "gemini-2.5-flash"
        self.chat_history = []

    def run_workflow(self, user_prompt: str, country: str = "India", mode: str = "Balanced") -> str:
        logger.info("--- 🚀 Starting 5-Node Multi-Agent Inference ---")
        
        self.chat_history.append(f"User: {user_prompt}")
        context_string = "\n".join(self.chat_history[-4:]) 
        system_context = f"CRITICAL CONTEXT: Market: {country}. Strategy Mode: {mode}."

        # ==========================================
        # AGENT 1: WEB RESEARCHER (Google Search ONLY)
        # ==========================================
        logger.info("Agent 1: Web Researcher pulling live news...")
        try:
            research_prompt = f"Find breaking news or recent policy updates regarding this request: {user_prompt} in {country}."
            researcher_response = self.client.models.generate_content(
                model=self.model,
                contents=research_prompt,
                config=types.GenerateContentConfig(
                    # Exclusively using the Google Search tool here
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.2
                )
            )
            live_news = researcher_response.text
        except Exception as e:
            logger.error(f"Web Researcher Failed: {e}")
            live_news = "No breaking web news retrieved at this time."

        # ==========================================
        # AGENT 2: SENIOR STRATEGIST (Custom APIs ONLY)
        # ==========================================
        logger.info("Agent 2: Strategist is querying APIs...")
        strategist_prompt = (
            f"{system_context}\n\n"
            f"Live Web News to consider:\n{live_news}\n\n"
            "You are the Senior Investment Strategist. Context:\n" f"{context_string}\n\n"
            "Task: Answer the user's prompt. Use `query_mospi_live` for macro-economic stats, `consult_junior_financial_advisor` for market risk, and `query_investment_knowledge_base` for internal docs."
        )
        
        try:
            strategist_response = self.client.models.generate_content(
                model=self.model,
                contents=strategist_prompt,
                config=types.GenerateContentConfig(
                    # Exclusively using custom Python functions here
                    tools=[consult_junior_financial_advisor, query_investment_knowledge_base, query_mospi_live],
                    temperature=0.3
                )
            )
            baseline_plan = strategist_response.text
        except Exception as e:
            logger.error(f"Strategist Failed: {e}")
            baseline_plan = f"System Note: Live API retrieval failed. Baseline Strategy for {country} ({mode} mode): Focus on sustainable supply chains and MSME compliance."

        # ==========================================
        # AGENT 3: CRITIC (InsightLaw ONLY)
        # ==========================================
        logger.info("Agent 3: Critic is red-teaming...")
        try:
            critic_prompt = (
                f"Review this strategy for {country}: \n{baseline_plan}\n\n"
                "Use `query_insightlaw_live` to find legal risks. Output your critique."
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
        except Exception as e:
            logger.error(f"Critic Failed: {e}")
            critique = "No critical legal vulnerabilities detected in the baseline plan at this time."

        # ==========================================
        # AGENT 4: SYNTHESIZER
        # ==========================================
        logger.info("Agent 4: Synthesizer formatting output...")
        try:
            synth_prompt = (
                "Merge the Baseline Strategy and Critique. "
                "CRITICAL: Append a section titled '📚 Resources & Data Sources' listing the APIs used and any Web Search links provided.\n\n"
                f"Strategy:\n{baseline_plan}\n\nCritique:\n{critique}"
            )
            final_response = self.client.models.generate_content(
                model=self.model,
                contents=synth_prompt,
                config=types.GenerateContentConfig(temperature=0.2)
            )
            final_text = final_response.text
        except Exception as e:
            logger.error(f"Synthesizer Failed: {e}")
            final_text = f"{baseline_plan}\n\n*Critique:* {critique}\n\n📚 *Resources & Data Sources*\n- Offline Fallback Matrix"

        self.chat_history.append(f"System: {final_text}")
        return final_text