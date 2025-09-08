Of course. Here is a comprehensive Low-Level Design (LLD) and implementation document for creating the powerful TAM Agent within the Google Agentspace ecosystem. This document is designed to be a step-by-step guide for the implementation team.

-----

## **Low-Level Design: TAM Co-Pilot Agent**

**Version:** 1.0
**Date:** September 8, 2025
**Author:** Gemini AI

### 1\. Overview

#### 1.1. Purpose

This document provides the detailed low-level design for the **TAM Co-Pilot Agent**. This agent is an AI-powered assistant built on Google Cloud to support Technical Account Managers (TAMs) by automating data gathering, providing proactive insights, and streamlining reporting.

#### 1.2. Scope

The solution will be delivered through the **Google Agentspace** platform. It will address the four primary activities of a TAM as identified in the project's source requirements:

1.  **Proactive Platform Health & Optimization**
2.  **Issue & Escalation Management**
3.  **Strategic Roadmap & Quarterly Business Reviews (QBRs)**
4.  **Product Adoption & Launch Support**

#### 1.3. Target Audience

This document is intended for Cloud Architects, Software Developers, and DevOps Engineers responsible for building, deploying, and maintaining the TAM Co-Pilot solution.

-----

### 2\. System Architecture

The TAM Co-Pilot follows a modular, serverless architecture orchestrated by Vertex AI Agent Builder and exposed through Agentspace.

**Architectural Flow:**

1.  A **Human TAM** interacts with the **TAM Co-Pilot** through the **Google Agentspace** web interface.
2.  Agentspace routes the user's prompt to the **Vertex AI Agent**.
3.  The **Vertex AI Agent** (LLM) interprets the user's intent and decides which tool(s) to use.
4.  The Agent invokes the appropriate tool:
      * For knowledge-based questions, it queries the **Vertex AI Search** knowledge base.
      * For data-driven tasks, it calls a specific **Cloud Function** via an HTTP request.
5.  The **Cloud Function** executes its logic, calling external Google Cloud APIs (e.g., Monitoring, BigQuery, Support).
6.  The Cloud Function returns a structured JSON response to the Vertex AI Agent.
7.  The Agent synthesizes the responses from all called tools into a natural language answer.
8.  The final answer is presented to the user in the Agentspace interface.

-----

### 3\. Component Deep Dive

#### 3.1. Google Agentspace (Frontend & User Experience Layer)

  * **Role:** Provides the secure, authenticated user interface for TAMs. It manages user sessions and renders the conversational experience.
  * **Configuration:**
      * **App Name:** `TAM Co-Pilot`
      * **Company Name:** As per organizational requirements.
      * **Identity Provider:** Google Identity (to ensure only authorized internal employees can access it).
      * **Connected Assistant:** The `tam-copilot-vertex-agent` will be configured as the primary assistant.
      * **Instructions:** High-level instructions for the Agentspace assistant will guide its persona and direct complex tasks to the connected Vertex AI Agent.

#### 3.2. Vertex AI Agent (Orchestration Core)

  * **Role:** The "brain" of the operation. It understands natural language, maintains conversation state, performs multi-turn reasoning, and orchestrates calls to various tools.
  * **Configuration:**
      * **Agent Name:** `tam-copilot-vertex-agent`
      * **Model:** `gemini-1.5-pro` (for advanced reasoning and large context).
      * **Agent Goal & Instructions:**
        ```
        You are 'TAM Co-Pilot,' an expert Google Cloud Technical Account Manager assistant. Your purpose is to provide data-driven, accurate, and concise information to help your human colleagues.
        - When a user asks for a summary or report, you MUST use multiple tools if necessary to gather all relevant information (e.g., for a health check, use tools for cost, performance, and security).
        - Always state the project ID and timeframe you are reporting on.
        - Never provide information you cannot verify with a tool. If you don't know, say so.
        - For technical questions, primarily use the 'answer_technical_question' tool to search the knowledge base.
        ```
      * **Tools:** The agent will be configured with the tools defined in section 4.2.

#### 3.3. Tool Layer (Cloud Functions)

  * **Role:** These are the "hands" of the agent. Each function is a serverless, single-purpose microservice that interacts with a specific Google Cloud API.
  * **Runtime:** Python 3.12
  * **Authentication:** All functions will be triggered via HTTP and secured with IAM, invokable only by the Vertex AI Agent's service account.

| Function Name (in code)     | Tool Name (in Agent)     | Description                                                                                             | Target APIs                                       |
| --------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `get_health_check`          | `get_platform_health`    | Retrieves a summary of a project's performance, cost, and security posture.                             | Monitoring, Billing, Security Command Center, Recommender |
| `get_support_cases`         | `get_open_support_cases` | Fetches a list and status of open support cases for a given customer account.                           | Cloud Support API                                 |
| `get_qbr_data`              | `generate_qbr_data`      | Gathers key metrics for a QBR, such as quarter-over-quarter cost trends and service usage highlights. | BigQuery, Billing API                             |
| `create_qbr_slides`         | `create_qbr_slides`      | (Advanced) Takes structured data from `generate_qbr_data` and populates a Google Slides template.       | Google Slides API, Google Drive API               |
| `answer_technical_question` | `answer_technical_question` | (Built-in Agent Tool) Queries the knowledge base to answer technical questions about Google Cloud services. | Vertex AI Search API                              |

#### 3.4. Knowledge Base (Vertex AI Search)

  * **Role:** Serves as the agent's long-term memory for unstructured data, enabling Retrieval-Augmented Generation (RAG).
  * **Configuration:**
      * **Data Store Type:** Unstructured Documents.
      * **Data Sources:**
        1.  **Google Cloud Storage Bucket:** To ingest internal PDFs, DOCX files such as customer-specific architectural diagrams, internal best practice guides, and post-mortems.
        2.  **Website URLs:** The entire `cloud.google.com/docs` and `cloud.google.com/blog` sites will be indexed to provide up-to-date public information.

#### 3.5. Data & Analytics Platform (BigQuery)

  * **Role:** The centralized data warehouse for historical and aggregated data, enabling trend analysis that is not possible with real-time APIs alone.
  * **Datasets & Tables:**
      * **Dataset:** `tam_agent_analytics`
      * **Table 1: `project_cost_and_usage_daily`**
          * **Purpose:** Stores daily snapshots of cost and key resource counts per project.
          * **Ingestion:** Populated daily by a scheduled Cloud Function that processes detailed billing export data.
      * **Table 2: `support_case_history`**
          * **Purpose:** Stores historical data on all support cases for trend analysis.
          * **Ingestion:** Populated via an event-driven Cloud Function triggered by new support case notifications.

-----

### 4\. Data Models & API Schemas

This section defines the precise contracts for the tools used by the Vertex AI Agent.

#### 4.1. Tool: `get_platform_health`

  * **Request Schema:**
    ```json
    {
      "type": "object",
      "properties": {
        "project_id": { "type": "string" },
        "time_period_days": { "type": "integer", "default": 7 }
      },
      "required": ["project_id"]
    }
    ```
  * **Response Schema (from Cloud Function):**
    ```json
    {
      "type": "object",
      "properties": {
        "project_id": { "type": "string" },
        "health_summary": {
          "performance_status": { "type": "string", "enum": ["OK", "Warning", "Critical"] },
          "cost_trend_percent": { "type": "number" },
          "new_critical_findings": { "type": "integer" },
          "optimization_recommendations": { "type": "integer" }
        }
      }
    }
    ```

#### 4.2. Tool: `get_open_support_cases`

  * **Request Schema:**
    ```json
    {
      "type": "object",
      "properties": {
        "customer_account_id": { "type": "string" }
      },
      "required": ["customer_account_id"]
    }
    ```
  * **Response Schema (from Cloud Function):**
    ```json
    {
      "type": "object",
      "properties": {
        "total_open_cases": { "type": "integer" },
        "p1_cases": { "type": "integer" },
        "cases": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "case_id": { "type": "string" },
              "title": { "type": "string" },
              "priority": { "type": "string" },
              "last_update": { "type": "string" }
            }
          }
        }
      }
    }
    ```

*... (Similar schemas would be defined for `generate_qbr_data` and other tools)*

-----

### 5\. Implementation Steps (Phased Approach)

**Phase 1: Foundation & Data Platform (1-2 Weeks)**

1.  **IAM & Project Setup:** Create a dedicated GCP project. Define and create IAM service accounts (`sa-tam-agent-functions`, `sa-vertex-agent`) with the principle of least privilege.
2.  **BigQuery Setup:** Create the `tam_agent_analytics` dataset and the tables defined in section 3.5.
3.  **Data Ingestion:** Set up the daily BigQuery billing export. Create and deploy the scheduled Cloud Function to populate the `project_cost_and_usage_daily` table.

**Phase 2: Core Capabilities - Health & Issues (2-3 Weeks)**

1.  **Develop Cloud Functions:** Implement, test, and deploy the `get_health_check` and `get_support_cases` Cloud Functions.
2.  **Build Knowledge Base:** Create the Vertex AI Search data store and begin ingesting public documentation.
3.  **Initial Agent Configuration:** Create the `tam-copilot-vertex-agent`. Configure its goal, instructions, and the two new Cloud Function tools, plus the Vertex AI Search tool.
4.  **Unit Testing:** Rigorously test the agent's ability to call these tools correctly via the Vertex AI console.

**Phase 3: Advanced Capabilities - QBR & Strategy (2 Weeks)**

1.  **Develop QBR Function:** Implement, test, and deploy the `get_qbr_data` Cloud Function, including complex SQL queries to BigQuery.
2.  **Enhance Knowledge Base:** Upload internal best-practice documents and customer-specific architectural diagrams to the Vertex AI Search GCS bucket.
3.  **Agent Integration:** Add the new `generate_qbr_data` tool to the agent. Refine agent instructions to handle more complex, multi-step queries.

**Phase 4: Frontend Integration & Deployment (1 Week)**

1.  **Agentspace Setup:** Create the Agentspace app as defined in section 3.1.
2.  **Connect Agent:** Connect the fully configured Vertex AI Agent to the Agentspace assistant.
3.  **End-to-End Testing:** Conduct thorough testing from the Agentspace UI to ensure the entire flow is working as expected.

**Phase 5: User Acceptance Testing (UAT) & Rollout (Ongoing)**

1.  **Onboard Pilot Users:** Grant a pilot group of TAMs access to the Agentspace app.
2.  **Gather Feedback:** Collect feedback on agent accuracy, usability, and missing features.
3.  **Iterate:** Use feedback to refine agent instructions, improve tool descriptions, and plan for new tool development (e.g., `create_qbr_slides`).

-----

### 6\. Security & IAM

  * **User Access:** Handled by Google Identity through Agentspace. Only members of a specific Google Group (e.g., `gcp-tams@yourcompany.com`) will have access.
  * **Service Account for Cloud Functions (`sa-tam-agent-functions`):** This service account will have the following roles:
      * `roles/monitoring.viewer`
      * `roles/billing.viewer`
      * `roles/securitycenter.viewer`
      * `roles/recommender.viewer`
      * `roles/cloudsupport.viewer`
      * `roles/bigquery.dataViewer`
      * `roles/bigquery.jobUser`
  * **Service Account for Vertex AI Agent:** This will be the default Vertex AI Custom Code Service Account, granted the `roles/cloudfunctions.invoker` role to be able to call the tool functions.
  * **Network Security:** All Cloud Functions will be configured with ingress settings to "Allow internal traffic and traffic from Cloud Load Balancing" to restrict public access. The Vertex AI Agent will access them through Google's internal network.

-----

### 7\. Appendix: Sample Cloud Function Snippet

*File: `main.py` (for `get_support_cases`)*

```python
import functions_framework
from google.cloud.support_v2 import CaseServiceClient
from google.api_core.client_options import ClientOptions

@functions_framework.http
def get_support_cases(request):
    """
    HTTP Cloud Function to get open support cases.
    Request JSON body: { "customer_account_id": "customers/12345" }
    """
    request_json = request.get_json(silent=True)
    if not request_json or 'customer_account_id' not in request_json:
        return ("Missing 'customer_account_id' in request body", 400)

    customer_id = request_json['customer_account_id']
    
    # Use regional endpoint as required by the API
    client_options = ClientOptions(api_endpoint="cloudsupport.googleapis.com")
    client = CaseServiceClient(client_options=client_options)

    # Filter for only open cases
    request_filter = 'state="OPEN"'
    
    try:
        response = client.list_cases(parent=customer_id, filter=request_filter)
        
        cases_list = []
        p1_count = 0
        for case in response:
            if case.priority == 'P1':
                p1_count += 1
            cases_list.append({
                "case_id": case.name.split('/')[-1],
                "title": case.display_name,
                "priority": case.priority.name,
                "last_update": str(case.update_time)
            })

        result = {
            "total_open_cases": len(cases_list),
            "p1_cases": p1_count,
            "cases": cases_list[:10] # Return max 10 for brevity
        }
        return (result, 200)

    except Exception as e:
        return ({"error": str(e)}, 500)

```