import os


class Config:
    ES_SCHEMA = 'http'
    ES_HOST = 'localhost'
    ES_PORT = 9200
    ES_PRODUCTS_INDEX_TEMPLATE = 'products'
    ES_PRODUCTS_INDEX_ALIAS = 'products'
    FILE_ATTRIBUTE_MAPPING = './data/attribute-labels.json'
    FILE_BRANDS = './data/brand-mapping.json'
    OPENAI_API_KEY = None

    def __init__(self):
        self.load_from_env()

    def load_from_env(self):
        """
        Load configuration from environment variables
        :return:
        """
        self.ES_SCHEMA = os.getenv('ES_SCHEMA', self.ES_SCHEMA)
        self.ES_HOST = os.getenv('ES_HOST', self.ES_HOST)
        self.ES_PORT = os.getenv('ES_PORT', self.ES_PORT)
        self.ES_PRODUCTS_INDEX_TEMPLATE = os.getenv('ES_PRODUCTS_INDEX_TEMPLATE', self.ES_PRODUCTS_INDEX_TEMPLATE)
        self.ES_PRODUCTS_INDEX_ALIAS = os.getenv('ES_PRODUCTS_INDEX_ALIAS', self.ES_PRODUCTS_INDEX_ALIAS)
        self.FILE_ATTRIBUTE_MAPPING = os.getenv('FILE_ATTRIBUTE_MAPPING', self.FILE_ATTRIBUTE_MAPPING)
        self.FILE_BRANDS = os.getenv('FILE_BRANDS', self.FILE_BRANDS)
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', self.OPENAI_API_KEY)

    def es_uri(self):
        return f'{self.ES_SCHEMA}://{self.ES_HOST}:{self.ES_PORT}'
