import requests

ALLOWED_DOMAINS = ["trusted-redirect.com", "partner.com"]

def validate_redirect_url(input_url: str):
    # Parse the user-provided URL
    parsed_url = requests.utils.urlparse(input_url)
    return parsed_url.geturl()

def perform_redirect(redirection_url: str):
    # Assume there's some method that performs a redirect
    print(f"Redirecting to: {redirection_url}")