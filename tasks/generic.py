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

translate = Translation("facebook/mbart-large-50-many-to-many-mmt", findmodels=False)
split_paragraphs = Segmentation(paragraphs=True)
split_sentences = Segmentation(sentences=True)

