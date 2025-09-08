from adk.api.tools import tool

@tool
def gmail_draft_tool(recipient: str, subject: str, body: str) -> str:
    """
    Creates a draft email in Gmail.
    In a real implementation, this would use the Gmail API.
    """
    print(f"TOOL: Creating Gmail draft for '{recipient}' with subject '{subject}'...")
    # Mock implementation
    return f"Successfully created email draft for '{recipient}'."

@tool
def google_chat_tool(message: str) -> str:
    """
    Sends a notification to a pre-configured Google Chat room via webhook.
    In a real implementation, this would make an HTTP POST request to the webhook URL.
    """
    print(f"TOOL: Sending Google Chat notification: '{message}'...")
    # Mock implementation
    return "Successfully sent notification to incident channel."

@tool
def google_slides_tool(customer_name: str, usage_data: str, crm_data: str) -> str:
    """
    Creates a new Google Slides presentation from a template for a QBR.
    It populates the slides with the provided data.
    In a real implementation, this would use the Google Slides API.
    """
    print(f"TOOL: Generating QBR presentation for '{customer_name}'...")
    # Mock implementation
    slide_url = "https://docs.google.com/presentation/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/edit"
    return f"Successfully created QBR presentation. Link: {slide_url}"
