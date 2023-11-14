# This file contains the workflow for the demo.
import json
import os
import textwrap
from typing import Any

import requests
from tasks.generic import translate, sentiment_analysis

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

    def identify_problem(self, complaint, options=None):
        """
        Identify the problem in a complaint.

        Parameters
        ----------
        inout : str
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

        if options is None:
            options = {}

        prompt = """
        You are a helpful fact-oriented assistant.
        Extract the problems behind the complaint.
        Keep the meaning of the input text. NEVER ADD OR REMOVE ANY INFORMATION.
        USE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.
        Instead of "The problem behind the complaint is that <problem>.", write "<problem>."
        Identify all problems. Output one problem per line.
        Don't presume anything. If no problems are stated explicitly, don't add them.

        Input text:
        "{complaint}"

        Output text:
        """

        print(f"Input: {complaint}")

        if options['with_translation']:
            print("Translating the complaint into English")
            complaint = translate(complaint, 'en', 'de')

        # Remove leading whitespace from the prompt lines
        prompt = "\n".join(line.strip() for line in prompt.splitlines())

        # Create the prompt from the template
        prompt = prompt.format(complaint=complaint)
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
            sentiment = sentiment_analysis(complaint)
            print("Sentiment: " + sentiment)
        else:
            sentiment = None

        return {
            'complaint': complaint,
            'problems': answer,
            'sentiment': sentiment,
            'prompt': prompt
        }

    def solve_problem(self, complaint, problems, sentiment, options=None):
        """
        Solve the problem in a complaint.

        Parameters
        ----------
        complaint : str
            The complaint to be processed.
        problems : list
            A list of problems identified in the complaint.
        sentiment : str
            The sentiment of the complaint.
        options : dict
            A dictionary of options for the processing.

        Returns
        -------
        solution : str
            The solution to the problem.
        """

        if options is None:
            options = {}

        prompt = """
        You are a helpful specialist in fixing (alleged) construction defects.
        You work the company that built the client's building.
        React empathically to the customer's complaint and provide an approach to solve each problem.
        Keep in mind, that the customer blames your employer for the problems, even if not stated directly in the original complaint.
        You want to help the customer, but you don't want to admit any guilt.
        DON'T REFER TO YOUR ROLE. You are inherently representing your employer's company.

        Problems:
        {problems}

        The original complaint was:
        "{complaint}"
        {sentiment}
        Write an email to the customer. Start with a message of empathy reflecting the sentiment of the complaint.
        Then, provide a solution for each problem. USE SIMPLE LANGUAGE WITHOUT SUBORDINATE CLAUSES.
        DON'T ASSUME ANYTHING ABOUT THE CAUSE OF THE PROBLEMS. If you can't draw the cause from the original complaint, ask the customer.
        Return just the email body, no subject.
        
        Output text:
        """

        print(f"Complaint: {complaint}")
        print(f"Problems: {problems}")
        print(f"Sentiment: {sentiment}")

        if options['with_sentiment']:
            sentiment_prompt = f"\nSentiment: {sentiment}\n"
        else:
            sentiment_prompt = ""

        # Remove leading whitespace from the prompt lines
        prompt = "\n".join(line.strip() for line in prompt.splitlines())

        # Create the prompt from the template
        prompt = prompt.format(complaint=complaint, problems=problems, sentiment=sentiment_prompt)
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
        try:
            answer = response["response"]
        except KeyError:
            print("KeyError: " + json.dumps(response))
            return {
                'error': "KeyError: no key named 'response' in " + json.dumps(response)
            }

        # Split the answer into paragraphs and wordwrap them to 80 characters
        print("\n\n".join([textwrap.fill(paragraph, 80) for paragraph in answer.split("\n\n")]))

        if options['with_translation']:
            print("Translating the answer into German")
            answer = translate(answer, 'de', 'en')

        return {
            'complaint': complaint,
            'problems': problems,
            'sentiment': sentiment,
            'answer': answer,
            'prompt': prompt
        }

