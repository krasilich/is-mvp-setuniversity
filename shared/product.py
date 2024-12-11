import time
from typing import Optional
from shared.config import Config
from elasticsearch import Elasticsearch
from openai import OpenAI


class Product:
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    brand_id: Optional[int] = None
    brand_name: Optional[str] = None
    url_key: Optional[str] = None
    attributes: Optional[dict] = None
    embedding_source: Optional[str] = None
    embedding: Optional[list] = None

    def __init__(self,
                 sku: str = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 category_id: Optional[int] = None,
                 category_name: Optional[str] = None,
                 brand_id: Optional[int] = None,
                 brand_name: Optional[str] = None,
                 url_key: Optional[str] = None,
                 attributes: Optional[dict] = None,
                 embedding_source: Optional[str] = None,
                 embedding: Optional[list] = None):
        self.sku = sku
        self.name = name
        self.description = description
        self.category_id = category_id
        self.category_name = category_name
        self.brand_id = brand_id
        self.brand_name = brand_name
        self.url_key = url_key
        self.attributes = attributes
        self.embedding_source = embedding_source
        self.embedding = embedding

    def generate_embedding_source(self):
        """
        Generate a text source for embedding
        :return:
        """
        attributesText = ''.join([f'{attr.get('label')}: {attr.get('value')}' for attr in self.attributes.values()])
        self.embedding_source = (f'SKU: {self.sku} Категорія: {self.category_name} Бренд: {self.brand_name}'
                                 f' Назва: {self.name} Опис: {self.description}'
                                 f' {attributesText}')

        return self.embedding_source


class ProductEmbedder:
    def __init__(self, config: Config):
        self.config = config
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)

    def embed(self, product: Product):
        product.embedding = self._embed(product)

    def _embed(self, product: Product):
        try:
            response = self.openai_client.embeddings.create(
                model='text-embedding-3-small',
                input=[product.embedding_source],
                encoding_format="float"
            )

            return response.data[0].embedding
        except:
            pass

        return None


class ProductRepository:
    def __init__(self, config: Config):
        self.config = config
        self.es_client = Elasticsearch([config.es_uri()])

    def get(self, sku: str) -> Product:
        raise NotImplementedError

    def save(self, product: Product):
        raise NotImplementedError

    def delete(self, sku: str):
        raise NotImplementedError

    def search_knn(self, embedding: list[float]) -> list:
        query = [{
            'field': 'embedding',
            'query_vector': embedding,
            'k': 5
        }]
        response = self.es_client.search(index=self.config.ES_PRODUCTS_INDEX_ALIAS, knn=query)

        products = []
        for hit in response['hits']['hits']:
            product = Product(**hit['_source'])
            products.append(product)

        return products


class ProductBatchIndexer:
    es_client = None
    config = None
    index_name = None
    batch_size = None
    batch = []

    def __init__(self, config: Config, batch_size: int = 1000):
        self.config = config
        self.batch_size = batch_size

    def initialize(self):
        self.es_client = Elasticsearch([self.config.es_uri()])
        self._create_index()

    def _create_index(self):
        """
        Create a new index for products
        """
        config = Config()
        self.index_name = f'{config.ES_PRODUCTS_INDEX_ALIAS}_{int(time.time())}'
        self.es_client.indices.create(index=self.index_name, body={
            'mappings': {
                'properties': {
                    'sku': {'type': 'keyword'},
                    'name': {'type': 'text'},
                    'description': {'type': 'text'},
                    'category_id': {'type': 'integer'},
                    'category_name': {'type': 'text'},
                    'brand_id': {'type': 'integer'},
                    'brand_name': {'type': 'text'},
                    'url_key': {'type': 'keyword'},
                    'attributes': {'type': 'object'},
                    'embedding_source': {'type': 'text'},
                    'embedding': {'type': 'dense_vector', 'dims': 1536}
                }
            }
        })
        self.es_client.indices.put_settings(index=self.index_name, body={
            'index': {
                'mapping': {
                    'total_fields.limit': 5000
                }
            }
        })

    def add(self, product: Product):
        self.batch.append(product)
        if len(self.batch) >= self.batch_size:
            self.flush()

    def flush(self):
        body = []
        for product in self.batch:
            body.append({'index': {'_index': self.index_name}})
            product_dict = {k: v for k, v in product.__dict__.items() if v is not None}

            body.append(product_dict)
        res = self.es_client.bulk(body=body, refresh=False)

        if res.body.get('errors'):
            failed_items = [item for item in res.body['items'] if item['index']['status'] != 201]
            error_messages = [item['index']['error']['reason'] for item in failed_items]

            raise Exception(f'Failed to index {len(failed_items)} products: {error_messages}')

        self.batch = []

    def switch_alias(self):
        self.es_client.indices.update_aliases(
            actions=[
                {'remove': {'index': '*', 'alias': self.config.ES_PRODUCTS_INDEX_ALIAS}},
                {'add': {'index': self.index_name, 'alias': self.config.ES_PRODUCTS_INDEX_ALIAS}}
            ]
        )
        self.es_client.indices.refresh(index=self.config.ES_PRODUCTS_INDEX_ALIAS)
