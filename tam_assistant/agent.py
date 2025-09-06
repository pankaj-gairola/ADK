from google.adk.agents.llm_agent import Agent
from tam_assistant import google_workspace
from google.adk.tools.tool import Tool
import base64
from email.mime.text import MIMEText

PROMPT_TEMPLATE = """
As a Technical Account Manager (TAM) Assistant, your primary role is to assist TAMs by drafting email replies to customers.

When a user provides you with a customer email and relevant context, you must follow these steps:
1.  **Analyze the customer's request:** Carefully read the customer's email to understand their needs, questions, or issues.
2.  **Consult relevant documents:** If context from documents is provided, thoroughly review them to gather the necessary information to address the customer's request. The documents are retrieved from Google Drive.
3.  **Draft a professional email reply:** Compose a clear, concise, and professional email.
    - Address the customer by name.
    - Acknowledge their request.
    - Provide a comprehensive answer or solution based on the provided documents.
    - If you need more information, ask clarifying questions.
    - Maintain a helpful and supportive tone.
4.  **Review and refine:** Before finalizing the draft, review it for clarity, accuracy, and tone.

You have access to the following tools to help you:
- A tool to read documents from Google Drive.
- A tool to read emails from Gmail.
- A tool to send emails via Gmail.

Remember, you are drafting an email on behalf of the TAM. The final email should be ready for the TAM to review and send.
"""

def list_drive_files(number_of_files: int = 10):
    """List files from Google Drive."""
    drive_service = google_workspace.get_drive_service()
    results = (
        drive_service.files()
        .list(pageSize=number_of_files, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])
    return items

def read_drive_file(file_id: str):
    """Read a file from Google Drive."""
    drive_service = google_workspace.get_drive_service()
    file = drive_service.files().get(fileId=file_id).execute()
    request = drive_service.files().get_media(fileId=file_id)
    file_content = request.execute()
    return {"name": file["name"], "content": file_content.decode("utf-8")}

def read_gmail_message(message_id: str):
    """Read a message from Gmail."""
    gmail_service = google_workspace.get_gmail_service()
    message = (
        gmail_service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    return message

def send_gmail_message(to: str, subject: str, message_text: str):
    """Send a message from Gmail."""
    gmail_service = google_workspace.get_gmail_service()
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"raw": raw_message}
    message = (
        gmail_service.users().messages().send(userId="me", body=body).execute()
    )
    return message

root_agent = Agent(
    model='gemini-1.5-flash',
    name='tam_assistant',
    description='A TAM assistant that replies to emails and refers to documents in Google Drive.',
    instruction=PROMPT_TEMPLATE,
    tools=[
        Tool(
            name="list_drive_files",
            description="List files from Google Drive.",
            func=list_drive_files,
        ),
        Tool(
            name="read_drive_file",
            description="Read a file from Google Drive.",
            func=read_drive_file,
        ),
        Tool(
            name="read_gmail_message",
            description="Read a message from Gmail.",
            func=read_gmail_message,
        ),
        Tool(
            name="send_gmail_message",
            description="Send a message from Gmail.",
            func=send_gmail_message,
        ),
    ],
)
