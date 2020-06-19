from lxml import etree


def check_classification(patent_data, patent_classes=['H']):
    """Проверка соответствия патенту заданным классам согласно МПК."""
    root = etree.fromstring(patent_data.encode('utf-8'))
    classifications = root.findall(".//classification-ipcr")
    if classifications:
            section = classifications[0].find(".//section")
            if(section.text in patent_classes):
                return True

    return False


def get_patent_name(patent_data):
    """Получить название патента."""
    root = etree.fromstring(patent_data.encode('utf-8'))
    doc_numers = root.findall(".//doc-number")
    countries = root.findall(".//country")
    patent_name = countries[0].text + doc_numers[0].text
    return patent_name

def get_patent_number(patent_data):
    """Получить название патента."""
    root = etree.fromstring(patent_data.encode('utf-8'))
    doc_numers = root.findall(".//doc-number")
    countries = root.findall(".//country")
    patent_name = countries[0].text + doc_numers[0].text
    return doc_numers[0].text


def get_claims(patent_data):
    """Получить claim'ы патента"""
    root = etree.fromstring(patent_data.encode('utf-8'))
    claims = root.findall(".//claim")
    if(claims):
        claims_without_tags = [''.join(claim.itertext()).strip() for claim in claims]
        return claims_without_tags

    return []


def get_invention_title(patent_data):
    """Получить название изобретения."""
    root = etree.fromstring(patent_data.encode('utf-8'))
    invention_title = root.findall(".//invention-title")
    return invention_title[0].text


def get_claim_name(index):
    """Получить имя claim'а."""
    return 'claim ' + str(index + 1)