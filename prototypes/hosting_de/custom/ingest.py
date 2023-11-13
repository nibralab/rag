import glob
import json
import os
import shutil
import sys
from hashlib import md5
from multiprocessing import Pool
from typing import List, Dict, Any

from langchain.document_loaders import UnstructuredMarkdownLoader
from tqdm import tqdm
from txtai.embeddings import Embeddings

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, "db")
SOURCE_PATH = os.path.join(BASE_PATH, "source_documents")

chunk_size = 500
chunk_overlap = 50


def load_single_document(file_path: str) -> List[Dict[str, Any]]:
    loader = UnstructuredMarkdownLoader(file_path)
    documents = loader.load()
    metadata = {}
    json_ = file_path.replace(".en.md", ".json")
    if os.path.exists(json_):
        with open(json_) as f:
            metadata = json.load(f)

    for document in documents:
        document.metadata["source"] = file_path.replace(SOURCE_PATH + "/", "").replace(".en.md", ".de.md")

    documents = [
        {
            "source": document.metadata["source"],
            "date": os.path.getmtime(file_path),
            "text": document.page_content,
            "slug": metadata.get("slug", None),
            "title": metadata.get("title", None),
            "tags": metadata.get("tags", []),
            "metadata": document.metadata,
        } for document in documents if document.page_content
    ]

    return documents


def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Dict[str, Any]]:
    """
    Loads all documents from the source documents directory, ignoring specified files
    """
    all_files = glob.glob(os.path.join(source_dir, f"**/*.en.md"), recursive=True)
    filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]

    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=160) as pbar:
            for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.extend(docs)
                pbar.update()

    return results


def process_documents(ignored_files: List[str] = []) -> List[Dict[str, Any]]:
    """
    Load documents and split in chunks
    """
    print(f"Loading documents from {SOURCE_PATH}")
    documents = load_documents(SOURCE_PATH, ignored_files)
    if not documents:
        print("No new documents to load")
        exit(0)
    print(f"Loaded {len(documents)} new documents from {SOURCE_PATH}")

    return documents


def main():
    embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2", "content": True})

    if os.path.exists(DATA_PATH):
        # Update and store locally vectorstore
        print(f"Appending to existing vectorstore at {DATA_PATH}")
        embeddings.load(DATA_PATH)

        # Set limit to maximum integer
        existing_documents = embeddings.search("SELECT DISTINCT source, date FROM txtai", 2**63-1)

        ignored_files = []
        for document in existing_documents:
            filename = os.path.join(SOURCE_PATH, document["source"])
            filename = filename.replace(".de.md", ".en.md")

            if os.path.exists(filename):
                file_date = os.path.getmtime(filename)
                if file_date == document["date"]:
                    ignored_files.append(filename)

        documents = process_documents(ignored_files)
    else:
        # Create and store locally vectorstore
        print("Creating new vectorstore")
        documents = process_documents()

    print(f"Creating embeddings. May take some minutes...")
    embeddings.upsert([
        (
            # Create an MD5 hash from the metadata to use as the ID
            md5(json.dumps(document["text"]).encode("utf-8")).hexdigest(),  # ID
            {
                "source": document["source"],
                "date": document["date"],
                "text": document["text"],
                "slug": document["slug"],
                "title": document["title"],
                "metadata": document["metadata"],
                "tags": document["tags"]
            },  # data
            None  # tags
        ) for document in documents
    ])

    embeddings.save(DATA_PATH)

    print(f"Ingestion complete!")


if __name__ == "__main__":
    # If command line option '--reset' is passed, delete the vectorstore
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print(f"Deleting existing vectorstore at {DATA_PATH}")

        # Remove the directory DATA_PATH
        shutil.rmtree(DATA_PATH)

    main()
