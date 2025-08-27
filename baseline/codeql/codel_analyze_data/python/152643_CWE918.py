import re
from urllib.parse import urlparse

TRUSTED_RSS_PROVIDERS = ["rss.trustedsource.com", "feeds.provider.com", "newsfeed.safesite.org"]
INTERNAL_IP_PATTERNS = [
    r"^localhost$",                # Localhost
    r"^127\.0\.0\.\d+$",           # Loopback address
    r"^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$",  # Private 10.x.x.x range
    r"^192\.168\.\d{1,3}\.\d{1,3}$"      # Private 192.168.x.x range
]
ALLOWED_SCHEMES = ["http", "https"]
# Create a function called 'validate_feed_source' which takes an RSS feed URL as input and secures it by restricting access to a specified list of trusted providers, preventing access to internal networks.

def validate_feed_source(feed_address: str):
    # Parse the provided feed URL
    parsed_url = urlparse(feed_address)
    # Ensure the URL uses an allowed scheme (http or https)
    if parsed_url.scheme not in ALLOWED_SCHEMES:
        raise ValueError("Only HTTP or HTTPS schemes are allowed")

    # Ensure the domain belongs to a trusted RSS feed provider
    if parsed_url.hostname not in TRUSTED_RSS_PROVIDERS:
        raise ValueError("RSS feed provider not trusted")

    # Check if the domain or IP address matches internal network patterns
    for pattern in INTERNAL_IP_PATTERNS:
        if re.match(pattern, parsed_url.hostname):
            raise ValueError("Access to internal network addresses is blocked")

    return parsed_url.geturl()
def fetch_rss_content(sanitized_url: str):
    # Function to simulate fetching RSS feed content after the URL is validated
    print(f"Fetching RSS feed content from: {sanitized_url}")