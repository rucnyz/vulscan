from xml.dom.minidom import parseString

def parse_xml_minidom(xml_data: str):
    dom = parseString(xml_data)
    config = {}
    for item in dom.getElementsByTagName('setting'):
        key = item.getAttribute('name')
        value = item.firstChild.nodeValue
        config[key] = value
    return config