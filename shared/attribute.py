import json


class Attribute:
    code: str
    label: str

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label


def from_json_file(file_path: str) -> dict:
    """
    Load attributes from JSON file
    :param file_path:
    :return: dict
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    return {attr['attribute_code']: Attribute(attr['attribute_code'], attr['frontend_label']) for attr in data}
