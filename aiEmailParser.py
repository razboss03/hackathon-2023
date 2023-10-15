import base64
import os
import time

import openai
from google_auth_httplib2 import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Set up the OpenAI API key
openai.api_key = "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"

# Import the necessary Gmail API libraries
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service(token_path):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_email_body(service, email_id):
    try:
        message = service.users().messages().get(userId='me', id=email_id).execute()
        if message:
            msg_str = base64.urlsafe_b64decode(message['payload']['parts'][0]['body']['data']).decode("utf-8")
            return msg_str
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def check_emails_for_keyword(service, keywords):
    print("Checking for emails with keywords...")
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    for message in messages:
        email_body = get_email_body(service, message['id'])
        if email_body:
            for keyword in keywords:
                if keyword in email_body:
                    return email_body

    return None

def main():

    # Replace 'YOUR_OPENAI_API_KEY' with your OpenAI API key
    openai.api_key = "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"

    keywords = ["confirm", "link"]

    service = get_gmail_service("ya29.a0AfB_byBp4sm_taihftINXZTyZzhMU4Hb9wYRKJTQbQzqYnUvALQKpnaT9VR5B0nor2OMl6SQ1G5ge1XRotKJVX3HqYfZMLSloRXgWWhOoj6uvA4zBMpSdlvvYORz2bjjXbO2Ta8aXweXHuJloFCyHW-R2YKh4kv2CwaCgYKAVASARESFQGOcNnCRO5yGfqcZJIYp9Zpwqb5cg0169")

    found_keyword = check_emails_for_keyword(service, keywords)

    if found_keyword:
        print(f"Most recent email with a keyword: {found_keyword}")
    else:
        print("Keyword not found in the first 5 emails.")

if __name__ == "__main__":
    main()
