import os.path
import base64
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail messages.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        main_list = [] 
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()         
            msg_id = msg['id']
            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            sender = headers.get('From', '')
            subject = headers.get('Subject', '')
            snippet = msg['snippet']
            date_received = headers.get('Date', '')
            
            main_list.append({
                "msg_id" : msg_id,
                "sender" : sender,
                "subject" : subject,
                "snippet" : snippet,
                "date_received" : date_received
            })
    return main_list