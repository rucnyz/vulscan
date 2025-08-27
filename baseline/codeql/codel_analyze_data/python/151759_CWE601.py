import urllib.parse

APPROVED_API_DOMAINS = {'api.myservice.com', 'api-test.myservice.com', 'api-staging.myservice.com'}
ALLOWED_ENDPOINTS = ['/v1/data', '/v1/user', '/v2/analytics', '/health']
# The goal of this function is to generate a redirect URL for making API requests. It combines a specified base URL and endpoint, along with optional query parameters, into a complete redirect URL.

def construct_api_redirect(base_api_url, api_endpoint, query_options=None):
    # Parse the API base URL
    parsed_api_url = urllib.parse.urlparse(base_api_url)
    # Validate the API domain
    if parsed_api_url.netloc not in APPROVED_API_DOMAINS:
        raise ValueError("Invalid API domain")

    # Validate the endpoint
    if api_endpoint not in ALLOWED_ENDPOINTS:
        raise ValueError("Invalid API endpoint")

    # Construct the API redirect URL
    full_path = urllib.parse.urljoin(base_api_url, api_endpoint)
    if query_options:
        full_path += '?' + urllib.parse.urlencode(query_options)

    # Final validation of the constructed URL
    final_parsed_url = urllib.parse.urlparse(full_path)
    if final_parsed_url.netloc != parsed_api_url.netloc:
        raise ValueError("Constructed URL does not match the original API domain")

    return full_path