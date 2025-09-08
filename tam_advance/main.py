import os
import time
from dotenv import load_dotenv

from adk.api import agents

# Import all our custom tools from their respective modules
from gcp_tools import gcp_monitoring_tool, gcp_billing_tool, gcp_usage_tool
from crm_tools import create_case_tool, get_customer_profile_tool
from communication_tools import gmail_draft_tool, google_chat_tool, google_slides_tool
from knowledge_tools import internal_knowledge_search_tool

# --- Agent Definition ---

TAM_SUPER_AGENT_INSTRUCTIONS = """
You are a world-class AI assistant for a Google Cloud Technical Account Manager.
Your purpose is to be a force multiplier, automating the administrative, data-gathering,
and initial drafting tasks across a TAM's four core responsibilities.

Analyze the user's high-level request and formulate a step-by-step plan to address it.
You must select the appropriate tools from your available toolset to execute your plan.
Think step-by-step. For each step, state which tool you will use and what parameters you will use.
After executing all steps, provide a final, concise summary of your actions and the results.
You must always prioritize human review; your final actions should be creating drafts,
summaries, or notifications, not sending communications or making changes directly.
"""

def create_tam_super_agent() -> agents.Agent:
    """Creates and configures the multi-capable TAM Super-Agent."""
    return agents.Agent(
        name="tam_super_agent",
        instructions=TAM_SUPER_AGENT_INSTRUCTIONS,
        tools=[
            # GCP Tools
            gcp_monitoring_tool,
            gcp_billing_tool,
            gcp_usage_tool,
            # CRM/Ticketing Tools
            create_case_tool,
            get_customer_profile_tool,
            # Communication Tools
            gmail_draft_tool,
            google_chat_tool,
            google_slides_tool,
            # Knowledge/RAG Tools
            internal_knowledge_search_tool,
        ],
    )

def run_agent_scenario(agent: agents.Agent, prompt: str, scenario_title: str):
    """Helper function to run and print a single agent scenario."""
    print("=" * 60)
    print(f"🎬 SCENARIO: {scenario_title}")
    print(f"👤 TAM PROMPT: \"{prompt}\"")
    print("-" * 60)
    
    start_time = time.time()
    response = agent.run(prompt)
    end_time = time.time()
    
    print("\n" + "-" * 20 + " AGENT FINAL SUMMARY " + "-" * 20)
    print(response)
    print(f"\n✅ SCENARIO COMPLETE (Execution time: {end_time - start_time:.2f} seconds)")
    print("=" * 60 + "\n\n")


# --- Main Execution Logic ---
if __name__ == "__main__":
    load_dotenv()
    print("🚀 Initializing Professional TAM Super-Agent...")
    
    # In a real application, this might be a web server or a Pub/Sub listener.
    # Here, we will run a series of predefined prompts to demonstrate capabilities.
    tam_agent = create_tam_super_agent()
    print("✅ Agent Initialized.")

    prompts_to_run = [
        {
            "title": "Proactive Health & Optimization",
            "prompt": "Run a proactive health and cost check for Customer X and draft an email to the internal engineering team with the findings."
        },
        {
            "title": "Issue & Escalation Management",
            "prompt": "We have a P1 incident for Customer Y regarding 'database latency'. Create a support case, notify the incident chat room, and check our knowledge base for post-mortems on similar issues."
        },
        {
            "title": "Strategic Roadmap & QBR",
            "prompt": "Prepare the Q2 2026 QBR deck for Customer Z."
        },
        {
            "title": "New Product Adoption & Launch Planning",
            "prompt": "A new service, 'AlloyDB Omni for Postgres', was just announced. Identify which of my customers are heavy Postgres users and draft an introductory email for them."
        }
    ]

    for scenario in prompts_to_run:
        run_agent_scenario(tam_agent, scenario["prompt"], scenario["title"])
        time.sleep(2) # Pause between scenarios for readability
