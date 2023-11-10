import json
import os
import re
import torch
from typing import List
from tqdm import tqdm
from generic_tasks.sentences import crop_bullet

from tasks.generic import translate,  split_paragraphs, split_sentences


def resilient_translate(text: str, target: str, source: str):
    try:
        return translate(text, target, source)
    except torch.cuda.OutOfMemoryError as e:
        print(f"Out of memory error: {e}\ntranslating\n'{text}'\nfrom '{source}' to '{target}'")
        print("Using original text instead.")
        return text


def all_documents(root_directory: str) -> List[str]:
    """
    Return all documents in a directory
    """
    documents = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            documents.append(os.path.join(root, file))
    return documents


def _handle_document(filename: str) -> str:
    if filename.startswith("original_documents/_"):
        return "skipped"

    if not filename.endswith(".de.md"):
        return "skipped"

    with open(filename, "r") as f:
        document = f.read()

    document, metadata = _parse_and_translate_document(document)

    if not document:
        return "skipped"

    document = document.strip() + "\n"

    # Repair translation issues
    document = document.replace("_BAR_", "|")
    document = re.sub(r"Special characters `.*$", "Special characters `(+-=.,:;_!?$#%&~^*|/()@{}[]<>)`", document)

    # Write document back to file
    target_file = filename.replace(".de.md", ".en.md")
    target_file = target_file.replace("original_documents", "source_documents")

    # Create directory, if it does not exist
    os.makedirs(os.path.dirname(target_file), exist_ok=True)

    # Write document to file
    with open(target_file, "w") as f:
        f.write(document)

    # Write meta data
    target_file = target_file.replace(".en.md", ".json")
    with open(target_file, "w") as f:
        json.dump(metadata, f, indent=4)

    return "cleaned"


def _translate_paragraph(paragraph, inside_code_block):
    bullet, paragraph = crop_bullet(paragraph)
    translated_paragraph = bullet
    for sentence in split_sentences(paragraph, "de"):
        # Unmask abbreviations
        sentence = sentence.replace("__PERIOD__", ".")

        # Skip code blocks
        if sentence.startswith("```"):
            translated_paragraph += sentence + "\n"

            inside_code_block = True
            if sentence.endswith("```"):
                inside_code_block = False

            continue

        if sentence.endswith("```") and inside_code_block:
            inside_code_block = False
            translated_paragraph += sentence + "\n"
            continue

        if inside_code_block:
            translated_paragraph += sentence + "\n"
            continue

        sentence = resilient_translate(sentence, "en", "de")

        # Add sentence to paragraph
        translated_paragraph += sentence + " "
    return translated_paragraph, bullet


def _parse_and_translate_document(document):
    parts = re.split(r"(?:^|\n)---(?:\n|$)", _normalize_document(document))
    document = ""
    meta_data = {}
    previous_bullet = ""
    for part in parts:

        if not part:
            continue

        if re.search(r"(?:^|\n)title:", part):
            key = None

            for line in part.split("\n"):
                line = line.strip()

                if not line:
                    continue

                if line.endswith(":"):
                    key = line[:-1]
                    meta_data[key] = []
                    continue

                if line.startswith("- ") and key is not None:
                    line_ = line[2:]
                    if key != "slug":
                        line_ = resilient_translate(line_, "en", "de")

                    meta_data[key].append(line_)
                    continue

                if line == "-":
                    continue

                key, value = re.search(r"(?:^|\n)([A-Za-z0-9_]+):[ ]*\"?(.*?)\"?$", line).groups()

                key = key.strip()
                value = value.strip()

                if len(value) > 0:
                    if key != "slug":
                        meta_data[key] = resilient_translate(value, "en", "de")
                    else:
                        meta_data[key] = value
                else:
                    meta_data[key] = ''

            continue

        # Replace placeholders in format '{{< param key >}}', if key is in meta_data
        for key, value in meta_data.items():
            # If value is a list, join it using ", "
            if isinstance(value, list):
                value = ", ".join(value)
            part = part.replace(f"{{{{< param {key} >}}}}", value)

        # print(f"\nPrepared part:\n{part}")

        inside_code_block = False

        for paragraph in split_paragraphs(part):
            translated_paragraph, bullet = _translate_paragraph(paragraph, inside_code_block)
            document += ("\n\n" if not bullet or bullet != previous_bullet else "\n") + translated_paragraph
            previous_bullet = bullet

    return document, meta_data


def _normalize_document(document):
    document = _normalise_newlines(document)
    # Replace placeholders
    document = re.sub(r"###[A-Z_]*###", "hosting.de", document)
    # Remove <br> tags
    document = document.replace("<br>", "\n")
    # Remove images (pattern: "![alt text](image.png)<br>")
    document = re.sub(r"!\[.*?]\(.*?\)", "", document)
    # Reduce multiple newlines to max. two newlines
    document = re.sub(r"[ \t]*\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", document)
    # Fix single space before bullet
    document = re.sub(r"\n[ ]\*", "\n*", document)
    # Collapse bullet lists
    for i in range(2):
        document = re.sub(r"([^|\n][ \t]*\*)(.+?)\n(?:[ \t]*\n)*([ \t]*\*)", "\g<1>\g<2>\n\n\g<3>", document)
    # Mask abbreviations
    document = re.sub(r"(bzw|etc|[Gg]gf|\.[A-ZÄÖÜa-zäöü])\.", "\g<1>__PERIOD__", document)
    return document


def _normalise_newlines(doc: str) -> str:
    """
    Ensure proper newlines
    """
    return doc.replace("\r\n?", "\n")


documents = all_documents("original_documents")
num_documents = len(documents)
cleaned = 0
skipped = 0

try:
    with tqdm(total=len(documents), desc='Cleaning documents', ncols=160) as pbar:
        for filename in documents:
            status = _handle_document(filename)
            if status == "cleaned":
                cleaned += 1

            pbar.update()

except KeyboardInterrupt:
    print("Stopped by user.")

skipped = num_documents - cleaned
print(f"\nCleaned {cleaned} documents, skipped {skipped} documents.")
