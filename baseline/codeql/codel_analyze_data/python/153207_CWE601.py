import re
from urllib import parse as urlparse

SCHEME_RE = re.compile(r"^[a-z]+:", re.I)
# This function ensures that a given url location value is converted into an absolute URL based on the request environment. If the value contains scheme keep as-is, otherwise add the provided scheme and hostname

def make_location_absolute(value, host_name, url_scheme):
    # If the value already has a scheme, return it as-is
    if SCHEME_RE.search(value):
        return value
    # If value starts with `//`, replace it with `/%2f` to avoid redirect issues
    if value.startswith("//"):
        value = "/%2f{}".format(value[2:])
    base_url = f"{url_scheme}://{host_name}"
    new_location = urlparse.urljoin(base_url, value)

    return new_location