# Professional TAM Super-Agent

## Overview
This project implements a sophisticated, multi-capable AI agent designed to assist a Technical Account Manager (TAM) with their core responsibilities. Built using the Google Agent Development Kit (ADK) in Python, this "Super-Agent" can plan and execute complex workflows across four key areas:

Proactive Health & Optimization: Analyzes customer cloud environments to identify performance and cost-saving opportunities.

Issue & Escalation Management: Acts as an assistant during incidents, automating communication and information retrieval.

Strategic Roadmap & QBRs: Gathers data and generates first drafts of Quarterly Business Review presentations.

New Product Adoption & Launch Planning: Proactively identifies customer opportunities for new products and drafts outreach communications.

The agent uses a modular, tool-based architecture. The central agent logic analyzes a TAM's natural language request and orchestrates a series of specialized tools to accomplish the goal.

> **Note:** This implementation uses mock tools that simulate API calls by printing to the console. This allows for easy demonstration of the agent's reasoning and planning capabilities without requiring real API credentials.

## Project Structure
.
├── main.py                 # Main execution script to run scenarios
├── agent.py                # Core agent definition and tool configuration
├── gcp_tools.py              # Tools for interacting with Google Cloud Platform
├── crm_tools.py              # Tools for interacting with CRM/Ticketing systems
├── communication_tools.py    # Tools for email, chat, and presentations
├── knowledge_tools.py        # Tools for searching internal documents (RAG)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables and configuration (create this yourself)
└── README.md                 # This file

## Setup and Installation
### 1. Prerequisites
Python 3.9+

### 2. Create the Environment File
Create a file named .env in the root of this project and add the following configuration. Fill in the placeholder values with your actual project details.

```
GCP_PROJECT_ID="your-gcp-project-id"

# Customer-specific GCP Project for analysis
CUSTOMER_GCP_PROJECT_ID="customer-production-project-id"

# Google Drive Folder ID for the Knowledge Base (RAG)
DRIVE_FOLDER_ID="your_drive_folder_id_for_documents"

# Google Slides Template ID for QBRs
QBR_TEMPLATE_ID="your_google_slides_template_id"

# Google Chat Webhook URL for incident notifications
CHAT_WEBHOOK_URL="your_google_chat_webhook_url"
```

### 3. Install Dependencies
Install all the required Python libraries using pip:

```bash
pip install -r requirements.txt
```

## How to Use the Agent
You interact with the agent by running the main script and providing it with a high-level task in natural language. The agent will print its plan, the tools it's using, the results from those tools, and its final summary.

Open a terminal and run the main.py script. It will cycle through four different example prompts, one for each of the agent's core capabilities.

```bash
python main.py
```

You can modify the prompts_to_run list in main.py to test your own commands.

### Example Prompts
*   **Health Check:** "Run a proactive health and cost check for Customer X and draft an email to the internal team with the findings."
*   **Escalation:** "We have a P1 incident for Customer Y regarding 'database latency'. Create a support case, notify the incident chat room, and check if we have any post-mortems on similar issues."
*   **QBR Prep:** "Prepare the Q2 2026 QBR deck for Customer Z using our standard template."
*   **Product Adoption:** "A new service, 'AlloyDB Omni for Postgres', was just announced. Identify which of my customers are heavy Postgres users and draft an introductory email for them."

## Future Enhancements
To make this agent production-ready, the mock tools in `gcp_tools.py`, `crm_tools.py`, etc., would be replaced with real implementations. This would involve:
1.  **Using Google Client Libraries:** Integrating libraries like `google-api-python-client` to call actual Google Cloud, Gmail, and Google Slides APIs.
2.  **Authentication:** Implementing a robust authentication flow (e.g., OAuth 2.0) to allow the agent to act on behalf of the user. This would require enabling the necessary APIs in a Google Cloud project and handling credentials securely.
3.  **Error Handling:** Adding comprehensive error handling and retry logic to the tool implementations for when API calls fail.