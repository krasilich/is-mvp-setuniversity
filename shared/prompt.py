import json
from typing import Optional

from openai import OpenAI

from shared.config import Config


class Prompt:
    openai_client: Optional[OpenAI] = None
    system_message = """
    You are a helpful shopping assistant in a grocery store.
    Translate the given prompt into Ukrainian. 
    Then extract product information such as names, weights, volumes, brands, categories and other attributes.
    Or try to identify the required ingredients for common dishes and extracts relevant product information.
    Extracted attribute names and values should be in ukrainian language, unless it`s a brand name or other non-translatable entity.
    Try to normalize the extracted information. For example weight should be in grams, volume in milliliters, etc.
    Respond with the extracted information only. Ensure that you return plain json without any formatting.
    JSON should contain an array of objects, where each object represents a product, even if there is only one product.
    Return an empty array if no products were extracted.
    Example for translated prompt: "Я хочу купити 1л молока Яготинське та масло"
    {
      "products": [
        {"Назва": "молоко", "Об'єм": "1000"},
        {"Назва": "масло"}
      ]
    }
    """

    def __init__(self, prompt: str, config: Config):
        self.prompt = prompt
        self.config = config

    def get_extractions(self):
        self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)

        response = (self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": self.prompt}
            ]
        ))

        try:
            extractions = response.choices[0].message.content
            extractions = json.loads(extractions)
            extractions = extractions.get('products', [])
        except Exception as e:
            extractions = []

        if not extractions:
            return extractions

        embeddings = []
        for extraction in extractions:
            embeddings.append(''.join([f'{key}: {value} ' for key, value in extraction.items()]))

        response = self.openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=embeddings,
            encoding_format="float"
        )

        for i, embedding in enumerate(response.data):
            extractions[i]['embedding'] = embedding.embedding

        return extractions
