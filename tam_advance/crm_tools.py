from adk.api.tools import tool

@tool
def create_case_tool(customer_name: str, priority: str, summary: str) -> str:
    """
    Creates a new support case in the case management system (e.g., Salesforce, Jira).
    In a real implementation, this would call the CRM's API.
    """
    print(f"TOOL: Creating new {priority} case for '{customer_name}' with summary: '{summary}'...")
    # Mock implementation
    case_id = "CASE-8675309"
    return f"Successfully created new support case. Case ID: {case_id}"

@tool
def get_customer_profile_tool(customer_name: str) -> str:
    """
    Retrieves a customer's profile from the CRM.
    This includes their business goals, tech stack, and key contacts.
    In a real implementation, this would call the CRM's API.
    """
    print(f"TOOL: Retrieving CRM profile for '{customer_name}'...")
    # Mock implementation
    if "Z" in customer_name:
         return "Customer 'Z' Profile:\n- Industry: Finance\n- Stated Goal: Reduce data processing costs by 20%.\n- Current Stack: Heavy use of self-managed Postgres on GCE, BigQuery."
    return "Customer Profile:\n- Industry: Retail\n- Stated Goal: Improve e-commerce checkout reliability.\n- Current Stack: GKE, Cloud SQL, Spanner."
