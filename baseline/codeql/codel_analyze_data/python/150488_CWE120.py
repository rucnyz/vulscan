permitted_versions = [b"2.0"]
def detect_ssh_version(incoming_data: bytes):
    if incoming_data.find(b"\n", incoming_data.find(b"SSH-")) == -1:
        raise ConnectionError("No SSH version string found")

    lines = incoming_data.split(b"\n")
    for line in lines:
        if line.startswith(b"SSH-"):
            remoteVersion = line.split(b"-")[1]
            if remoteVersion not in permitted_versions:
                raise ValueError(f"Unsupported SSH version: {remoteVersion}")
            i = lines.index(line)
            incoming_data = b"\n".join(lines[i + 1:])
            return incoming_data
    return incoming_data