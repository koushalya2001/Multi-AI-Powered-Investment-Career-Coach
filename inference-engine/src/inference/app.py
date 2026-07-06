import streamlit as st
import logging
from src.inference.workflow import MultiAgentSystem

# Configure page
st.set_page_config(page_title="AI Investment & Career Strategist", page_icon="📈", layout="wide")

# Initialize backend system only once per session
if "agent_system" not in st.session_state:
    st.session_state.agent_system = MultiAgentSystem()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome. I am your AI Strategist. Ask me about MSME manufacturing, AI career trends, or market risks. I will cross-reference live government data and corporate policies to build your strategy."}
    ]

st.title("📈 AI Investment & Career Strategist")
st.markdown("Powered by **Gemini 2.5 Flash**, **MoSPI MCP**, **InsightLaw**, and **Agent Garden**.")

# Helper function to render messages cleanly with minimizable resources
def render_message(role, content):
    with st.chat_message(role):
        # Check if the AI appended the Resources section
        if role == "assistant" and "📚 Resources & Data Sources" in content:
            # Split the content into the Main Strategy and the Resources block
            parts = content.split("📚 Resources & Data Sources")
            main_text = parts[0].strip()
            resources_text = parts[1].strip() if len(parts) > 1 else ""

            # 1. Display the main strategy text
            st.markdown(main_text)
            
            # 2. Tuck the resources into a minimizable expander
            if resources_text:
                with st.expander("📚 View Resources & Data Sources (Click to expand)", expanded=False):
                    st.markdown(resources_text)
        else:
            # Standard rendering for user messages or intro text
            st.markdown(content)

# Display chat history on reload
for message in st.session_state.messages:
    render_message(message["role"], message["content"])

# Chat input mechanism
if prompt := st.chat_input("E.g., Evaluate the legal and market risks of starting an MSME in green tech..."):
    
    # 1. Save and render User Input
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    # 2. Generate and render AI Response
    with st.spinner("Initiating Multi-Agent Workflow (Orchestrator ➔ Strategist ➔ Critic ➔ Synthesizer)..."):
        try:
            # Call the workflow
            full_response = st.session_state.agent_system.run_workflow(prompt)
            
            # Save to state
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Render the newly generated message (which will parse and collapse the resources)
            render_message("assistant", full_response)
            
        except Exception as e:
            error_msg = f"System Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})