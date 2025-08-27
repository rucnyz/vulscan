TRUSTED_DEVICE_SIGNATURES = {
    "device001": "89ebf76ae45bfcf6dd7f2aa3de8b20b3",
    "device002": "1dcfa479db7aae3d40b3984cdf202de6"
}

# Simulated function to receive a data packet from the IoT device
def get_data_packet(dev_id: str):
    if dev_id in TRUSTED_DEVICE_SIGNATURES:
        return {"temperature": 22.5, "humidity": 60}
    else:
        raise ConnectionError(f"Failed to receive packet from device {dev_id}")
def process_data_packet(dev_id: str, sign: str, payload: dict):
    try:
        packet = get_data_packet(dev_id)
        return packet
    except ConnectionError:
        return None