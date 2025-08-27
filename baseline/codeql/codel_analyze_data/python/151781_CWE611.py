import defusedxml.ElementTree as ET

def parse_xml_minidom(xml_data: str):
    root = ET.fromstring(xml_data)
    config = {}
    for item in root.findall('setting'):
        key = item.get('name')
        value = item.text
        config[key] = value
    return config