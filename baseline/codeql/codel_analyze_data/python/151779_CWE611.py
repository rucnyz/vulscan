from lxml import etree

def parse_xml_lxml(xml_data: str):
    try:
        parser = etree.XMLParser(resolve_entities=False, no_network=True)
        root = etree.fromstring(xml_data, parser=parser)

        config = {}
        for item in root.xpath('//setting'):
            key = item.get('name')
            value = item.text
            config[key] = value
        return config
    except etree.XMLSyntaxError as e:
        print(f"XML syntax error: {e}")
    except etree.DocumentInvalid as e:
        print(f"XML validation error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return {}