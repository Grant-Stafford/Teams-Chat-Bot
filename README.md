# Teams Chat Bot

## Overview

The `Teams Chat Bot.py` script monitors Azure Active Directory (Entra AD) applications for expiring secrets or certificates and sends notifications to a Microsoft Teams channel using a webhook. This helps administrators proactively manage expiring credentials and maintain application security.

## Features

1. **Authentication**:
   - Authenticates with Azure AD using the Microsoft Authentication Library (MSAL) and the Client Credentials flow.

2. **Application Monitoring**:
   - Retrieves all Azure AD applications and checks for expiring secrets or certificates within the next 30 days.

3. **Teams Notification**:
   - Sends a summary of applications with expiring credentials to a Microsoft Teams channel via a webhook.

## Prerequisites

1. **Azure AD App Registration**:
   - Create an App Registration in Azure AD with the following API permissions:
     - `Application.Read.All`
     - `Directory.Read.All`
     - `Organization.Read.All`
   - No redirect URI is required since the script uses the Client Credentials flow.

2. **Microsoft Teams Webhook**:
   - Set up an incoming webhook in the desired Teams channel. Follow the guide [here](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

3. **Environment Configuration**:
   - Replace the placeholders in the script with your actual Azure AD Tenant ID, Client ID, Client Secret, and Teams Webhook URL.

## Usage

1. Update the following variables in the script:
   - `TENANT_ID`: Your Azure AD Tenant ID.
   - `CLIENT_ID`: Your App Registration Client ID.
   - `CLIENT_SECRET`: Your App Registration Client Secret.
   - `TEAMS_WEBHOOK_URL`: Your Teams Webhook URL.

2. Run the script using Python:
   ```bash
   python Teams Chat Bot.py
   ```

3. Monitor the console output for progress and error messages.

## Expected Output

- **Console Output**:
  - Authentication success or failure.
  - Status of application retrieval and processing.
  - Status of the Teams message delivery.

- **Teams Notification**:
  - A message card listing applications with secrets or certificates expiring within the next 30 days.

## Notes

- Ensure the account running the script has sufficient permissions to access Azure AD resources.
- Test the script in a development environment before using it in production.
- Rotate the `CLIENT_SECRET` every 365 days to maintain security.

## Disclaimer

This script is provided as-is and should be used in compliance with your organization's security and governance policies.

