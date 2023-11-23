import os
import re

import requests
import torch
from transformers import pipeline
from txtai.pipeline import Translation, Segmentation, Labels


def sentiment_analysis(text):
    """
    Perform sentiment analysis on a text.

    The text is analyzed for five emotions (joy, sadness, anger, fear, love, surprise, neutral).
    The strongest emotion is returned as the sentiment of the text.

    Parameters
    ----------
    text : str
        The text to be processed.

    Returns
    -------
    sentiment : str
        The sentiment of the text.
    """

    labels = Labels("facebook/bart-large-mnli")
    tags = ["joy", "sadness", "anger", "fear", "love", "surprise", "neutral"]

    return tags[labels(text, tags)[0][0]]


def translate(text, target="en", source=None):
    """
    Translates text from source language into target language.

    This method supports texts as a string or a list. If the input is a string,
    the return type is string. If text is a list, the return type is a list.

    Args:
        texts: text|list
        target: target language code, defaults to "en"
        source: source language code, detects language if not provided

    Returns:
        list of translated text
    """

    if source is None:
        source = "en"

    if source == target:
        return text

    model_name = os.environ.get('MODEL_NAME')
    languages = {
        "en": "English",
        "de": "German",
    }

    prompt = f"""
    Translate the following text from {languages[source]} to {languages[target]} without adding any comments or notes:
    Text: {text}
    Translation:
    """
    prompt = re.sub(r"\n\s+", "\n", prompt)

    request = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    # Send the request to the Ollama URL
    ollama_url = os.environ.get("OLLAMA_URL", "http://ollama")
    ollama_port = os.environ.get("OLLAMA_PORT", "11434")
    ollama_url = f"{ollama_url}:{ollama_port}/api/generate"
    response = requests.post(ollama_url, json=request)

    # Get the response as JSON
    response = response.json()

    # Get the answer from the response
    answer = response["response"] if 'response' in response else response

    print("Orginal text: " + text)
    print("Translated text: " + answer)

    return answer


split_paragraphs = Segmentation(paragraphs=True)
split_sentences = Segmentation(sentences=True)
