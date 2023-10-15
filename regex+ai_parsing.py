import openai
import re

openai.api_key = "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"

# Example: this is a mock function that represents fetching the email body content
# In a real-world scenario, you need proper authentication and user consent before accessing their data
def mock_fetch_email_content():
    # This should be replaced with actual logic to fetch email content
    return """
    Dear user,
    
    Please click the link below to verify your account:
    https://example.com/verify?code=12345
    a
    Thank you!
    """

def find_verification_link(email_content):
    # Use a regular expression to find URLs in the email content
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_content)

    # Check each URL to see if it's a verification link
    for url in urls:
        prompt = f"This is a URL extracted from an email: {url}. Determine if this is a verification link."
        
        # Note: In a real application, you need to handle API keys and other credentials securely
        # Also, handle rate limits, timeouts, and errors appropriately
        response = openai.ChatCompletion.create(

          model="gpt-3.5-turbo",
          messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        # Interpret the model's response
        if "verification" in response['choices'][0]['message']['content']:
            return url

    return "No verification link found"

# Mock function to simulate fetching the email content
email_content = mock_fetch_email_content()
verification_link = find_verification_link(email_content)
print(verification_link)
