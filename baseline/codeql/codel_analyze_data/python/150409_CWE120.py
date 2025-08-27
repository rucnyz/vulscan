acceptable_http_headers = [b"HTTP/1.1"]
def process_http_request(request_data: bytes):
    if len(request_data) > 8192:
        raise ValueError("HTTP header longer than 8KB. Preventing denial of service attack.")

    if request_data.find(b"\r\n\r\n") == -1:
        raise ValueError("No complete HTTP header found")

    headers = request_data.split(b"\r\n")
    for line in headers:
        if line.startswith(b"HTTP/"):
            headerVersion = line.split(b" ")[0]
            if headerVersion not in acceptable_http_headers:
                raise ValueError(f"Unsupported HTTP version: {headerVersion}")
            i = headers.index(line)
            request_data = b"\r\n".join(headers[i + 1:])
            return request_data
    return request_data