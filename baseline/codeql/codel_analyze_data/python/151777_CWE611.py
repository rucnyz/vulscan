def parse_xml_config(xml_data: str):
    import defusedxml.ElementTree as ET
    root = ET.fromstring(xml_data)
    config = {}
    for item in root.findall('setting'):
        key = item.get('name')
        value = item.text
        config[key] = value
    return config