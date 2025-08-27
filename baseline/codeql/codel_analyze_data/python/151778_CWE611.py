from lxml import etree

def parse_xml_lxml(xml_data: str):
    try:
        root = etree.fromstring(xml_data)

        config = {}
        for item in root.xpath('//setting'):
            key = item.get('name')
            value = item.text
            config[key] = value
        return config
    except Exception as e:
        print(f"Unexpected error: {e}")
    return {}