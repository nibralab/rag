import json
import os
import re
from typing import Any

import requests
import torch
from dotenv import load_dotenv
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from txtai.embeddings import Embeddings

from tasks.generic import translate, sentiment_analysis

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_PATH)), "models")
DATA_PATH = os.path.join(BASE_PATH, "db")
ENV_PATH = os.path.join(BASE_PATH, ".env")

load_dotenv(ENV_PATH)
model_name = os.environ.get('MODEL_NAME')
model_n_ctx = os.environ.get('MODEL_N_CTX')
model_n_batch = int(os.environ.get('MODEL_N_BATCH', 8))
callbacks = []


class Workflow:

    def call(self, function_name: str, **params: dict[str, Any]) -> dict[str, Any]:
        # If this class has a function named func, call it
        func = getattr(self, function_name)
        if callable(func):
            return func(**params)

        return {
            'error': f'Unknown callable {function_name}'
        }

    def _prompt(self, request: str, sentiment: str = None) -> str:
        sentiment_modifier = ""
        if sentiment is not None and sentiment != "neutral":
            sentiment_modifier = f"Be empathic and take into account the sentiment '{sentiment}' of the request.\n"

        prompt = f"""
        Answer the following request using the context below.
        {sentiment_modifier}
        Question: {request}
        Context: 
        """

        return re.sub(r"\n\s+", "\n", prompt)

    def generate(self, support_request, options):
        """
        """

        print(f"Support Request: {support_request}")

        if options['with_translation']:
            print("Translating the request into English")
            support_request = translate(support_request, 'en', 'de')

        if options['with_sentiment']:
            print("Analyzing the sentiment of the request")
            sentiment = sentiment_analysis(support_request)
        else:
            sentiment = None

        # Retrieve the most similar texts from the database
        embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2", "content": True})
        embeddings.load(DATA_PATH)
        escaped_request = re.sub(r"([\"'])", r"\\\1", support_request)
        reference = embeddings.search(f"SELECT * FROM txtai WHERE similar('{escaped_request}') ORDER BY score DESC LIMIT 1")[0]
        context = reference['text']
        score = reference['score']
        data = json.loads(reference['data'])

        prompt = self._prompt(support_request, sentiment)
        ollama_url = "http://localhost:11434/api/generate"
        request = {
            "model": model_name,
            "prompt": prompt + context,
            "stream": False,
        }

        # Send the request to the Ollama URL
        response = requests.post(ollama_url, json=request)

        # Get the response as JSON
        response = response.json()

        # Get the answer from the response
        answer = response["response"]

        print("Got the answer: \n" + (answer if answer else "---"))

        return {
            "suggestion": translate(answer, 'de', 'en') if options['with_translation'] else answer,
            "helpdesk_url": "https://www.hosting.de/support/" + (data['slug'] if 'slug' in data else ''),
            'sentiment': sentiment,
            'prompt': prompt,
            'context': reference
        }