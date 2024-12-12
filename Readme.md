# IS MVP

Simple yet powerful shopping assistant for grocery stores based on OpenAI APIs.

## Features

Accepts such kind of prompts:
 
- "I need to buy some apples"
- "I'd like to buy 1L of olive oil, eggs and sosages of [specific brand]"
- "Products for a ceasar salad"

And returns a list of products in the store that match the prompt.

## Architecture
As a main data source we take a products feed which include some information about products and their categories. 
For each product vector representation is calculated using OpenAI API. 
Together with the product vector we index product data to the ElasticSearch. 
When user sends a request, we use OpenAI API to extract products information from the prompt.
Extracted information goes through the same process as the products feed data, and we get a vector representation of the user request.
Then we use ElasticSearch to find the most similar products to the user request vector.

## Prerequisites
To run the project you need to have Docker installed on your machine.
OpenAI API key is required to run the project.

OpenAI API key should be placed in the `docker-compose.yml` in `OPENAI_API_KEY` environment variable.

## CLI
Run container
```bash
docker compose build cli
docker compose up -d cli
docker compose exec cli sh  
```

Inside the container run the following command to list all available commands
```bash
python cli/cli.py --help
```

ElasticSearch snapshot with indexed data is provided by request.
Download the snapshot and unarchive it to the `elasticsearch/backup` folder.
So you should have the following structure
```
|-- elasticsearch
|   |-- backup
|       |-- is_snapshot
```

After first project start please run the following command to restore the snapshot
```bash
docker compose exec elasticsearch /usr/local/bin/restore.sh
```

But in case you want to reindex the data, you can run the following command.
This might take up to 12 hours to index all the data.
```bash
python cli/cli.py index-products [path_to_products_feed]
```

To execute a request run the following command
```bash
python cli/cli.py prompt "[prompt]"
```

## API
Not implemented yet

## Frontend
Not implemented yet
