import re
import socket

TRUSTED_DOMAINS = ["trustedsource.com", "safeprovider.com", "feeds.safesite.com"]
INTERNAL_IP_REGEX = [
    re.compile(r"^localhost$"),
    re.compile(r"^127\.0\.0\.\d+$"),
    re.compile(r"^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
    re.compile(r"^192\.168\.\d{1,3}\.\d{1,3}$")
]
ALLOWED_PROTOCOLS = ["http", "https"]
ALLOWED_PORTS = [80, 443]

def validate_url(feed_address: str):
    # Check if the URL contains a scheme
    if "://" not in feed_address:
        raise ValueError("Invalid URL format, missing protocol (http or https)")

    # Split the URL into scheme and the rest
    scheme, rest = feed_address.split("://", 1)

    # Check if the scheme is allowed
    if scheme not in ALLOWED_PROTOCOLS:
        raise ValueError(f"Only {', '.join(ALLOWED_PROTOCOLS)} schemes are allowed")

    # Split the rest into hostname and path
    host_and_path = rest.split("/", 1)
    hostname_with_port = host_and_path[0]

    # Split hostname and port if present
    if ":" in hostname_with_port:
        hostname, port = hostname_with_port.split(":", 1)
        port = int(port)
        if port not in ALLOWED_PORTS:
            raise ValueError(f"Only ports {', '.join(map(str, ALLOWED_PORTS))} are allowed")
    else:
        hostname = hostname_with_port
        port = 80 if scheme == "http" else 443

    # Check if the hostname is trusted
    if hostname not in TRUSTED_DOMAINS:
        raise ValueError("RSS feed provider is not trusted")

    # Check if the hostname matches any internal IP patterns
    for pattern in INTERNAL_IP_REGEX:
        if pattern.match(hostname):
            raise ValueError("Access to internal network addresses is blocked")

    # Resolve the hostname to an IP address and check if it is internal
    ip_address = socket.gethostbyname(hostname)
    for pattern in INTERNAL_IP_REGEX:
        if pattern.match(ip_address):
            raise ValueError("Access to internal network addresses is blocked")

    return feed_address

def retrieve_rss_data(sanitized_url: str):
    print(f"Retrieving RSS feed data from: {sanitized_url}")