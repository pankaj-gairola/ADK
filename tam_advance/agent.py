from adk.api import agents

# Import all our custom tools from their respective modules
from .gcp_tools import gcp_monitoring_tool, gcp_billing_tool, gcp_usage_tool
from .crm_tools import create_case_tool, get_customer_profile_tool
from .communication_tools import gmail_draft_tool, google_chat_tool, google_slides_tool
from .knowledge_tools import internal_knowledge_search_tool

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
