# This file contains the workflow for the demo.

import os
from typing import Any

import requests
from generic_tasks import sentiment_analysis, translate

ollama_url = os.environ.get("OLLAMA_URL", "http://localhost")
ollama_port = os.environ.get("OLLAMA_PORT", "11434")
ollama_url = f"{ollama_url}:{ollama_port}/api/generate"


class Workflow:

    def call(self, function_name: str, **params: dict[str, Any]) -> dict[str, Any]:
        # If this class has a function named func, call it
        func = getattr(self, function_name)
        if callable(func):
            return func(**params)

        return {
            'error': f'Unknown callable {function_name}'
        }

    def rephrase(self, input, options):
        """
        Identify the problem in a complaint.

        Parameters
        ----------
        complaint : str
            The complaint to be processed.
        options : dict
            A dictionary of options for the processing.

        Returns
        -------
        problems : list
            A list of problems identified in the complaint.
        sentiment : str
            The sentiment of the complaint.
        """

        prompt = """
        You are a helpful fact-oriented assistant.
        Extract the problems behind the complaint.
        Keep the meaning of the input text. NEVER ADD OR REMOVE ANY INFORMATION.
        USE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.
        Instead of "The problem behind the complaint is that <problem>.", write "<problem>."
        Identify all problems. Output one problem per line.
        Don't presume anything. If no problems are stated explicitly, don't add them.

        Input text:
        "{input}"
        
        Output text:
        """

        print(f"Input: {input}")

        if options['with_translation']:
            print("Translating the input into English")
            input = translate(input, 'de', 'en')

        # Create the prompt from the template
        prompt = prompt.format(input=input)
        print("Created the prompt: " + prompt)

        # Prepare the request for Ollama
        request = {
            "model": "llama2",
            "prompt": prompt,
            "options": {
                "temperature": 0.0,
            },
            "stream": False,
        }

        # Send the request to Ollama
        response = requests.post(ollama_url, json=request)

        # Get the response as JSON
        response = response.json()

        # Get the answer from the response
        answer = response["response"]

        # Split the answer into lines and remove leading and trailing whitespace
        answer = [line.strip() for line in answer.splitlines()]

        # Remove empty entries
        answer = [line for line in answer if line]

        print("Got the answer from the chain: \n" + "\n".join(answer))

        if options['with_sentiment']:
            print("Analyzing the sentiment of the input")
            sentiment, score = sentiment_analysis(input)
            print("Sentiment: " + sentiment)
        else:
            sentiment = None

        return {
            'input': input,
            'answer': answer,
            'sentiment': sentiment,
            'prompt': prompt
        }
