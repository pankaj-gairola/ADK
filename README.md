# ADK (Agent Development Kit)

This project contains a collection of agents built using the Agent Development Kit (ADK).

## Agents

*   **TAM Assistant:** An agent that helps Technical Account Managers (TAMs) by drafting email replies to customers. It can read documents from Google Drive and interact with Gmail.
*   **User Story Agent:** An agent that helps product owners write user stories.

## Setup

### Prerequisites

*   Python >= 3.11
*   `uv` package manager

### Installation

1.  Clone the repository.
2.  Install the dependencies:

    ```bash
    uv pip sync pyproject.toml
    ```

### TAM Assistant Setup

To use the TAM Assistant, you need to get your `credentials.json` file from the Google Cloud Console.

**Step 1: Create a new project in the Google Cloud Console**

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  If you don't have a project already, you will be prompted to create one. If you have existing projects, you can create a new one by clicking the project dropdown in the top navigation bar and then clicking "New Project".
3.  Give your project a name (e.g., "TAM Assistant") and click "Create".

**Step 2: Enable the Google Drive and Gmail APIs**

1.  Go to the [Google Cloud API Library](https://console.cloud.google.com/apis/library).
2.  Search for "Google Drive API" and click on it. Then, click the "Enable" button.
3.  Go back to the API Library, search for "Gmail API", click on it, and click the "Enable" button.

**Step 3: Configure the OAuth consent screen**

1.  In the left navigation menu, go to "APIs & Services" > "OAuth consent screen".
2.  Choose the user type. For this project, you can choose "External" and click "Create".
3.  Fill in the required information:
    *   **App name:** TAM Assistant
    *   **User support email:** Your email address
    *   **Developer contact information:** Your email address
4.  Click "Save and Continue".
5.  On the "Scopes" page, you don't need to add any scopes. Click "Save and Continue".
6.  On the "Test users" page, add your own email address as a test user. This will allow you to test the application while it's in development. Click "Save and Continue".
7.  Review the summary and click "Back to Dashboard".

**Step 4: Create an OAuth 2.0 Client ID**

1.  In the left navigation menu, go to "APIs & Services" > "Credentials".
2.  Click "+ CREATE CREDENTIALS" and select "OAuth client ID".
3.  For the "Application type", select "Desktop app".
4.  Give the client ID a name (e.g., "TAM Assistant Client").
5.  Click "Create".
6.  A window will pop up with your client ID and client secret. Click "DOWNLOAD JSON" to download the `credentials.json` file.

**Step 5: Place the `credentials.json` file in your project**

1.  Rename the downloaded file to `credentials.json`.
2.  Move the `credentials.json` file to the `d:\project\gcp\ADK\tam_assistant\` directory.

After you have completed these steps, you will be able to run the agent and it will be able to authenticate with your Google account.
