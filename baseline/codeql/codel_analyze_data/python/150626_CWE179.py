import re
from html import unescape

script_pattern = re.compile(r'<script.*?>.*?</script>', re.IGNORECASE | re.DOTALL)
on_event_pattern = re.compile(r'\s+on\w+\s*=', re.IGNORECASE)
def sanitize_html(html_content: str) -> str:
    # Remove script tags
    sanitized = script_pattern.sub('', html_content)
    # Remove on* event attributes
    sanitized = on_event_pattern.sub(' ', sanitized)
    return sanitized