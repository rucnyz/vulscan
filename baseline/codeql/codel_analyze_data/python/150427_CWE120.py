necessary_headers = ["Host", "User-Agent"]
def handle_http_headers(packet: bytes):
    if len(packet) > 8192:
        raise ValueError("HTTP headers too long. Preventing buffer overflow.")

    headers = packet.decode('utf-8').split("\r\n")
    collected_headers = {}
    for header_line in headers:
        if header_line == "":
            continue
        header_parts = header_line.split(": ")
        if len(header_parts) != 2:
            raise ValueError("Malformed header line")

        header_name, header_value = header_parts
        collected_headers[header_name] = header_value

    for necessary_header in necessary_headers:
        if necessary_header not in collected_headers:
            raise ValueError(f"Missing necessary header: {necessary_header}")

    return collected_headers