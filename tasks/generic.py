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


def translate(text: str, target="en", source=None):
    translator = Translation("facebook/mbart-large-50-many-to-many-mmt", findmodels=False)
    try:
        return translator(text, target=target, source=source)
    except torch.cuda.OutOfMemoryError as e:
        # Split the text into paragraphs
        paragraphs = split_paragraphs(text)
        if len(paragraphs) > 1:
            # Translate each paragraph individually
            print("Running into out-of-memory, splitting into paragraphs")
            translated_paragraphs = [translate(paragraph, target=target, source=source) for paragraph in paragraphs]
            return "\n\n".join(translated_paragraphs)
        else:
            # Split the text into sentences
            sentences = split_sentences(text)
            if len(sentences) > 1:
                # Translate each sentence individually
                print("Running into out-of-memory, splitting into sentences")
                translated_sentences = [translate(sentence, target=target, source=source) for sentence in sentences]
                return " ".join(translated_sentences)
            else:
                # Cannot split into smaller parts without losing meaning
                print("Running into out-of-memory, returning untranslated text")
                return text


split_paragraphs = Segmentation(paragraphs=True)
split_sentences = Segmentation(sentences=True)
