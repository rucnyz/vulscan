from urllib import parse as urlparse

ALLOWED_DOMAINS = ['trusted-site.com', 'partner-domain.org']
# This function is designed to create a URL to which a user will be redirected after logging in. It forms the full redirect URL by combining the base application URL with the 'next' parameter supplied by the user.

def generate_redirect_uri(auth_base_url, post_login_param):
    parsed_base = urlparse.urlparse(auth_base_url)
    base_domain = parsed_base.netloc
    # Combine auth_base_url with post_login_param to create the redirect URL
    redirect_url = urlparse.urljoin(auth_base_url, post_login_param)
    
    # Parse the resulting redirect URL
    parsed_redirect = urlparse.urlparse(redirect_url)
    redirect_domain = parsed_redirect.netloc

    # Check if the redirect domain is the same as the base domain or in the allowed list
    if redirect_domain == base_domain or redirect_domain in ALLOWED_DOMAINS:
        return redirect_url
    else:
        raise ValueError("Invalid redirect URL: not in the same domain or allowed list")