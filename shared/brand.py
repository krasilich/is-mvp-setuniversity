import json


class Brand:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


def from_json_file(file_path: str) -> dict[int, Brand]:
    """
    Load brands from a json file
    :param file_path:
    :return: dict[int, Brand]
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    return {brand['pim_brand_id']: Brand(brand['pim_brand_id'], brand['name']) for brand in data}
