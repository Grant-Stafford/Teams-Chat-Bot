'''
Pre-Reqs:
- You will need to create an App Registration with a Client Secret, as well as a Teams chat and webhook for the chat befor making this script work.
- NOTE: you DO NOT need a redirect URI for this script since it uses the Client Credentials flow, which is designed for server-to-server communication without user interaction.
So you can skip that part when creating the App Registration. Just make sure to set the API permissions correctly.

API Permissions:
Type:
- Application (Not Delegated)

Permissions needed: 
- Organization.Read.All (to read applications in your Azure AD tenant)
- Application.Read.All (to read applications in your Azure AD tenant)
- Directory.Read.All (to read directory data, including applications and their secrets/certificates)

Creating App Registration and Webhook:
- How to Make an App Registration in Azure AD: https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app?tabs=certificate%2Cexpose-a-web-api
- How to make a Teams WebHook: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=newteams%2Cdotnet
'''

# Things to Import
import msal
import requests
from datetime import datetime, timedelta
import json
import re

# Azure AD Authentication Configuration
TENANT_ID = "<Your Tenant ID>" # Replace with your Azure AD Tenant ID
CLIENT_ID = "<Your Client ID>" # Replace with your App Registration Client ID
CLIENT_SECRET = "<Your Client Secret>"  # Replace with your App Registration Client Secret every 365 days
SCOPES = ["https://graph.microsoft.com/.default"]
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
TEAMS_WEBHOOK_URL = "<Your Teams WebHook>" # Replace with your Teams Webhook URL
# Note: Make sure to replace the placeholders above with your actual Azure AD Tenant ID, Client ID, Client Secret, and Teams Webhook URL.

# Authenticate with Microsoft Graph using Client Credentials
app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}", client_credential=CLIENT_SECRET
)
token_response = app.acquire_token_for_client(scopes=SCOPES)

if "access_token" in token_response:
    access_token = token_response["access_token"]
    print("Authentication to Azure was successful")
else:
    print("Authentication to Azure failed:", token_response)
    exit()

# Prepare the request headers with the access token
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

# Make the GET request to retrieve applications
r = requests.get(f"{GRAPH_API_ENDPOINT}/applications", headers=headers)

# Prepare the message for Teams
teams_message = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "text": "Applications with expiring secrets or certificates within 30 days:\n"
}

# Check the response status code
if r.status_code == 200:
    print("Successfully retrieved applications")
    applications = r.json().get("value", [])
    
    # Get the current time and calculate the future time (30 days from now)
    current_time = datetime.utcnow()  # Use `datetime.now()` for local time if needed
    future_time = current_time + timedelta(days=30)  # Time 30 days from now
    
    # Loop through each application and check if it has secrets or certificates
    for app in applications:
        app_id = app["id"]
        app_name = app.get("displayName", "No name provided")
        
        # Check if the application has any password credentials (secrets)
        secret_r = requests.get(f"{GRAPH_API_ENDPOINT}/applications/{app_id}/passwordCredentials", headers=headers)
        if secret_r.status_code == 200:
            secrets = secret_r.json().get("value", [])
            if secrets:
                for secret in secrets:
                    secret_expiry = secret.get("endDateTime")
                    if secret_expiry:
                        try:
                            expiry_date = datetime.strptime(secret_expiry, "%Y-%m-%dT%H:%M:%S.%fZ")
                        except ValueError:
                            match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6})\d*Z", secret_expiry)
                            if match:
                                expiry_date = datetime.strptime(match.group(1) + "Z", "%Y-%m-%dT%H:%M:%S.%fZ")
                            else:
                                expiry_date = datetime.strptime(secret_expiry, "%Y-%m-%dT%H:%M:%SZ")
                        
                        # Check if the expiration date is within the next 30 days
                        if current_time <= expiry_date <= future_time:
                            days_left = (expiry_date - current_time).days
                            message = f"- **App**: {app_name} ({app_id}) has a secret that expires in **{days_left} days**."
                            teams_message["text"] += f"\n{message}"
        
        # Check if the application has any key credentials (certificates)
        cert_r = requests.get(f"{GRAPH_API_ENDPOINT}/applications/{app_id}/keyCredentials", headers=headers)
        if cert_r.status_code == 200:
            certificates = cert_r.json().get("value", [])
            if certificates:
                for cert in certificates:
                    cert_expiry = cert.get("endDateTime")
                    if cert_expiry:
                        try:
                            expiry_date = datetime.strptime(cert_expiry, "%Y-%m-%dT%H:%M:%S.%fZ")
                        except ValueError:
                            match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6})\d*Z", cert_expiry)
                            if match:
                                expiry_date = datetime.strptime(match.group(1) + "Z", "%Y-%m-%dT%H:%M:%S.%fZ")
                            else:
                                expiry_date = datetime.strptime(cert_expiry, "%Y-%m-%dT%H:%M:%SZ")
                        
                        # Check if the expiration date is within the next 30 days
                        if current_time <= expiry_date <= future_time:
                            days_left = (expiry_date - current_time).days
                            message = f"- **App**: {app_name} ({app_id}) has a certificate that expires in **{days_left} days**."
                            teams_message["text"] += f"\n{message}"
        else:
            print(f"Error retrieving certificates for {app_name} ({app_id}). Status: {cert_r.status_code}")
    
    # Send the message to the Teams Webhook
    response = requests.post(TEAMS_WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(teams_message))
    
    if response.status_code == 200:
        print("Successfully sent message to Teams.")
    else:
        print(f"Failed to send message to Teams. Status code: {response.status_code}")
else:
    print("Failed to retrieve applications. Error:", r.status_code, r.text)

# End of Script

'''
Expected Output:
Authentication to Azure was successful
Successfully retrieved applications
Successfully sent message to Teams.

Note: The Teams message will contain a list of applications with secrets or certificates that expire within the next 30 days.
'''
