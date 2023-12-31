import requests
import base64
import time
from html.parser import HTMLParser
from bs4 import BeautifulSoup


# Custom HTML parser to find links
# class LinkParser(HTMLParser):
#     def handle_starttag(self, tag, attrs):
#         if tag == 'a':
#             for attr in attrs:
#                 if attr[0] == 'href':
#                     self.link = attr[1]


def list_emails(oauth_token):
    # Set up the API endpoint
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

    # Prepare headers for the request
    headers = {
        "Authorization": f"Bearer {oauth_token}",
    }

    # Prepare the parameters for the request (in this case, max results)
    params = {
        "maxResults": 10,  # number of emails to list
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


# Function to get the full email details
def get_email_details(oauth_token, email_id):
    # Set up the API endpoint
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}?format=full"

    # Prepare headers for the request
    headers = {
        "Authorization": f"Bearer {oauth_token}",
    }

    # Make the GET request to the Gmail API
    response = requests.get(url, headers=headers)

    # If the request is successful
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Function to decode email parts
def decode_email_parts(parts):
    email_body = ""
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/html' and 'data' in part['body']:
                email_body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                email_body += decode_email_parts(part['parts'])
    return email_body


# Function to parse the email details for keywords and return the count
def parse_email_for_keywords(email_data, keywords):
    email_body = decode_email_parts(email_data.get('payload', {}).get('parts', []))
    return sum(keyword in email_body for keyword in keywords), email_body


# Function to find the confirmation link in the email body
def gen_links_list(email_body):
    # parser = LinkParser()
    # parser.feed(email_body)
    # return getattr(parser, "link", None)
    links = []
    soup = BeautifulSoup(email_body, 'html.parser')
    all_links = soup.find_all('a')
    for link in all_links:
        href = link.get('href')
        if href:
            links.append(href)
    return links

def find_conf_link_or_code(email_body):



# Function to periodically check emails for keywords
def check_emails_for_keywords(oauth_token, check_interval, timeout, keywords):
    start_time = time.time()
    best_match = None
    most_keywords_found = 0

    while True:
        emails = list_emails(oauth_token)
        if emails is not None:
            for email in emails["messages"]:
                email_data = get_email_details(oauth_token, email['id'])
                if email_data:
                    keyword_count, email_body = parse_email_for_keywords(email_data, keywords)
                    if keyword_count > most_keywords_found:
                        most_keywords_found = keyword_count
                        best_match = email_data
                        confirmation_links = gen_links_list(email_body)
                        print(confirmation_links)

                        # If we have found a good match, return the details
                        if most_keywords_found > 0:
                            headers = best_match['payload']['headers']
                            subject = next(header['value'] for header in headers if header['name'].lower() == 'subject')
                            time2 = next(header['value'] for header in headers if header['name'].lower() == 'received')
                            # print(time2)
                            from_email = next(header['value'] for header in headers if header['name'].lower() == 'from')

                            return {
                                "email_address": from_email,
                                "subject": subject,
                                "confirmation_link": confirmation_links
                            }

        # Check if the timeout has been reached
        if time.time() - start_time > timeout:
            return best_match  # Return the best match we found before timeout

        # Wait for the specified interval before checking again
        time.sleep(check_interval)


# Usage
oauth_token = "ya29.a0AfB_byCdM3wy7IchikfFsdKiGqZV60WWumqhFNjzru0QPbkIvqq4X-ivGqvBtRmX-yKRWZRT4Tqc5jRJYJ2JU56WSKdW_v4qJnaw0kUuWZBOi05BZcrvlg97x_cOTFfCiO50ic17b6EYWJytgdAb8oSZJy1vgYMvPooaCgYKAZcSARESFQGOcNnCKTuiQs3X_WkxdaH1uiYQNA0170"  # Replace with your actual OAuth token
check_interval = 60  # seconds
timeout = 3600  # 1 hour, for example
keywords = ["confirmation", "verify", "subscribe", "candidate", "email address"]  # Keywords to look for

email_details = check_emails_for_keywords(oauth_token, check_interval, timeout, keywords)
if email_details:
    print(f"Email address: {email_details['email_address']}")
    print(f"Subject: {email_details['subject']}")
    print(f"Confirmation link: {email_details['confirmation_link']}")
else:
    print("No email was found with the specified keywords within the timeout period.")
