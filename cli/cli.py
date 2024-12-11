import click
import ijson

from shared.attribute import from_json_file as attribute_from_json_file
from shared.brand import from_json_file as brand_from_json_file
from shared.config import Config
from shared.product import Product, ProductBatchIndexer, ProductEmbedder, ProductRepository
from shared.prompt import Prompt


@click.group(no_args_is_help=True)
def cli():
    """IS CLI Application"""
    pass


@cli.command()
@click.argument('file', type=click.File('r'))
def index_products(file):
    """
    Index products from a JSON file to Elasticsearch.
    Uses OpenAI API to create product embeddings
    """
    click.echo('Indexing products...')

    config = Config()
    attributes = attribute_from_json_file(config.FILE_ATTRIBUTE_MAPPING)
    brands = brand_from_json_file(config.FILE_BRANDS)
    product_embedder = ProductEmbedder(config)
    product_batch_indexer = ProductBatchIndexer(config, batch_size=100)
    try:
        product_batch_indexer.initialize()
    except:
        click.echo('Failed to initialize Elasticsearch client')
        return

    ijson.items(file, 'products.item')
    i = 0

    for productData in ijson.items(file, 'products.item'):
        productAttributes = {}

        if 'pim_brand_id' in productData:
            brand = brands.get(productData['pim_brand_id'])

            if brand:
                productData['brand_name'] = brand.name
                productData['brand_id'] = brand.id
            del productData['pim_brand_id']

        for key, value in productData.items():
            if not hasattr(Product, key):
                attribute = attributes.get(key)

                if not attribute:
                    continue

                productAttributes[key] = {'label': attribute.label, 'value': value}

        product = Product(productData['sku'], productData['name'], productData['description'],
                          int(productData['category_id']),
                          productData['category_name'], int(productData.get('brand_id', 0)),
                          productData.get('brand_name', ''),
                          productData['url_key'], productAttributes)
        product.generate_embedding_source()
        product_embedder.embed(product)

        if not product.embedding:
            click.echo(f'Failed to embed product {product.sku}')

        try:
            product_batch_indexer.add(product)

            click.echo(f'Total {i} products processed')
            i += 1
        except Exception as e:
            click.echo(e)

        # if i >= 100:
        #     break

    product_batch_indexer.flush()
    product_batch_indexer.switch_alias()

    click.echo('Products indexed successfully')


@cli.command()
@click.argument('prompt', type=str)
def prompt(prompt):
    """
    Get the prompt from user and try to find similar products
    """
    product_repository = ProductRepository(Config())
    prompt = Prompt(prompt, Config())
    extractions = prompt.get_extractions()

    if not extractions:
        click.echo('No products extracted')
        return

    for extraction in extractions:
        embedding = extraction.get('embedding')
        del extraction['embedding']

        if not embedding:
            click.echo(f'No embedding found for {extraction}')
            continue

        products = product_repository.search_knn(embedding)

        if not products:
            click.echo(f'No similar products found for {extraction}')
            continue

        click.echo(f'Similar products for {extraction}:')
        for product in products:
            click.echo(f'SKU: {product.sku} - {product.name}')


if __name__ == '__main__':
    cli()
