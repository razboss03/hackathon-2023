import requests
import time
import base64
from html.parser import HTMLParser


def get_email_body(oauth_token, email_id):
   print("get")
   # Set up the API endpoint
   url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}"


   # Prepare headers for the request
   headers = {
       "Authorization": f"Bearer {oauth_token}",
   }


   # Make the GET request to the Gmail API
   response = requests.get(url, headers=headers)


   # If the request is successful
   if response.status_code == 200:
       # Parse the JSON response
       email_data = response.json()


       # The email body is in the "parts" of the payload
       # Emails can be in different formats, so this is a simplistic approach
       # Depending on the email structure, you might need to parse different parts
       parts = email_data.get('payload', {}).get('parts', [])
       for part in parts:
           if part['mimeType'] == 'text/plain':
               # Decode the base64-encoded email body
               email_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
               return email_body
   return None


def list_emails(oauth_token):
   print("list")
   # Set up the API endpoint
   url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"


   # Prepare headers for the request
   headers = {
       "Authorization": f"Bearer {oauth_token}",
   }


   # Prepare the parameters for the request (in this case, max results)
   params = {
       "maxResults": 3,  # number of emails to list
   }


   # Make the GET request to the Gmail API
   response = requests.get(url, headers=headers, params=params)


   # If the request is successful
   if response.status_code == 200:
       # Parse the JSON response
       emails = response.json()
       return emails
   else:
       return None








def parse_email_for_keyword(email_body, keywords):
   print("parse")
   increment = 0;
   for keyword in keywords:
       if keyword in email_body:
           print(increment++1)
           return keyword
   return None




def check_emails_period(oauth_token, check_interval, timeout, keywords):
   print("email period")
   start_time = time.time()
   while True:
       emails = list_emails(oauth_token)
       if emails is not None:
           for email in emails["messages"]:
               email_body = get_email_body(oauth_token,email["id"])
               if email_body:
                   found_keyword = parse_email_for_keyword(email_body, keywords)
                   if found_keyword:
                       return found_keyword
   if time.time() - start_time > timeout:
       print("Timeout reached. Keyword not found.")
       return None


   print(f"Waiting for {check_interval} seconds before checking again ...")
   time.sleep(check_interval)




# Use the functions
oauth_token = "ya29.a0AfB_byCdM3wy7IchikfFsdKiGqZV60WWumqhFNjzru0QPbkIvqq4X-ivGqvBtRmX-yKRWZRT4Tqc5jRJYJ2JU56WSKdW_v4qJnaw0kUuWZBOi05BZcrvlg97x_cOTFfCiO50ic17b6EYWJytgdAb8oSZJy1vgYMvPooaCgYKAZcSARESFQGOcNnCKTuiQs3X_WkxdaH1uiYQNA0170"  # Replace with your actual OAuth token
check_interval = 60
timeout = 3600
keywords = ["verification", "confirm", "welcome", "verify", "confirmation", "candidate", "email", "email address"]


found_keyword = check_emails_period(oauth_token, check_interval, timeout, keywords)
if found_keyword:
   print(f"Keyword found: {found_keyword}")
else:
   print("Keyword not found within the timeout period.")