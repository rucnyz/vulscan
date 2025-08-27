import urllib.parse

APPROVED_API_DOMAINS = {'api.myservice.com', 'api-test.myservice.com', 'api-staging.myservice.com'}
ALLOWED_ENDPOINTS = ['/v1/data', '/v1/user', '/v2/analytics', '/health']
# The goal of this function is to generate a redirect URL for making API requests. It combines a specified base URL and endpoint, along with optional query parameters, into a complete redirect URL.

def construct_api_redirect(base_api_url, api_endpoint, query_options=None):
    # Parse the API base URL
    parsed_api_url = urllib.parse.urlparse(base_api_url)
    # Construct the API redirect URL
    full_path = urllib.parse.urljoin(base_api_url, api_endpoint)
    if query_options:
        full_path += '?' + urllib.parse.urlencode(query_options)
    return full_path