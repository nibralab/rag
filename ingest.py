#!/usr/bin/env python3
import json
import os
import glob
from typing import List
from dotenv import load_dotenv
from multiprocessing import Pool

from langchain.embeddings.ollama import OllamaEmbeddings
from tqdm import tqdm

from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from txtai import Embeddings

from constants import CHROMA_SETTINGS
import chromadb
from chromadb.api.segment import API
from generic_tasks import OllamaEmbedder

# Load environment variables
load_dotenv()
CUSTOM_NAME = os.environ.get('CUSTOM_DIR', 'demo')
CUSTOM_DIR = os.path.join('prototypes', CUSTOM_NAME)
persist_directory = os.environ.get('PERSIST_DIRECTORY', os.path.join(CUSTOM_DIR, 'db'))
source_directory = os.environ.get('SOURCE_DIRECTORY', os.path.join(CUSTOM_DIR, 'source_documents'))
chunk_size = 500
chunk_overlap = 50


# Custom document loaders
class MyElmLoader(UnstructuredEmailLoader):
    """Wrapper to fall back to text/plain when default does not work"""

    def load(self) -> List[Document]:
        """Wrapper adding fallback for elm without html"""
        try:
            try:
                doc = UnstructuredEmailLoader.load(self)
            except ValueError as e:
                if 'text/html content not found in email' in str(e):
                    # Try plain text
                    self.unstructured_kwargs["content_source"] = "text/plain"
                    doc = UnstructuredEmailLoader.load(self)
                else:
                    raise
        except Exception as e:
            # Add file_path to exception message
            raise type(e)(f"{self.file_path}: {e}") from e

        return doc


# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    # ".docx": (Docx2txtLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".eml": (MyElmLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}


def load_single_document(file_path: str) -> List[Document]:
    ext = "." + file_path.rsplit(".", 1)[-1].lower()
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
    """
    Loads all documents from the source documents directory, ignoring specified files
    """
    all_files = []
    for ext in LOADER_MAPPING:
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext.lower()}"), recursive=True)
        )
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext.upper()}"), recursive=True)
        )
    filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]

    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=160) as pbar:
            for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.extend(docs)
                pbar.update()

    return results


def process_documents(ignored_files: List[str] = []) -> List[Document]:
    """
    Load documents and split in chunks
    """
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory, ignored_files)
    if not documents:
        print("No new documents to load")
        exit(0)
    print(f"Loaded {len(documents)} new documents from {source_directory}")

    # Linearize list entries
    for document in documents:
        if 'emphasized_text_contents' in document.metadata:
            document.metadata['emphasized_text_contents'] = ' '.join(document.metadata['emphasized_text_contents'])
        if 'emphasized_text_tags' in document.metadata:
            document.metadata['emphasized_text_tags'] = ' '.join(document.metadata['emphasized_text_tags'])
        if 'link_urls' in document.metadata:
            document.metadata['link_urls'] = ' '.join(document.metadata['link_urls'])
        if 'link_texts' in document.metadata:
            document.metadata['link_texts'] = ' '.join(document.metadata['link_texts'])

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = text_splitter.split_documents(documents)
    print(f"Split into {len(documents)} chunks of text (max. {chunk_size} tokens each)")
    return documents


def batch_chromadb_insertions(chroma_client: API, documents: List[Document]) -> List[Document]:
    """
    Split the total documents to be inserted into batches of documents that the local chroma client can process
    """
    # Get max batch size.
    max_batch_size = chroma_client.max_batch_size
    for i in range(0, len(documents), max_batch_size):
        yield documents[i:i + max_batch_size]


def does_vectorstore_exist(persist_directory: str, embeddings: OllamaEmbeddings) -> bool:
    """
    Checks if vectorstore exists
    """
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    if not db.get()['documents']:
        return False
    return True


def main():
    # Create embeddings
    embeddings = Embeddings()

    # Chroma client
    chroma_client = chromadb.PersistentClient(settings=CHROMA_SETTINGS, path=persist_directory)

    if does_vectorstore_exist(persist_directory, embeddings):
        # Update and store locally vectorstore
        print(f"Appending to existing vectorstore at {persist_directory}")
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS,
                    client=chroma_client)
        collection = db.get()
        documents = process_documents([metadata['source'] for metadata in collection['metadatas']])
        print(f"Creating embeddings. May take some minutes...")
        add_documents_to_chromadb(db, batch_chromadb_insertions(chroma_client, documents))
    else:
        # Create and store locally vectorstore
        print("Creating new vectorstore")
        documents = process_documents()
        print(f"Creating embeddings. May take some minutes...")
        # Create the db with the first batch of documents to insert
        batched_chromadb_insertions = batch_chromadb_insertions(chroma_client, documents)
        created = False
        while not created:
            try:
                first_insertion = next(batched_chromadb_insertions)
                db = Chroma.from_documents(first_insertion, embeddings, persist_directory=persist_directory,
                                           client_settings=CHROMA_SETTINGS, client=chroma_client)
                created = True
            except ValueError as e:
                print(f"Error: {e}\nSkipping this batch of documents")
                print(first_insertion)
                continue

        # Add the rest of batches of documents
        add_documents_to_chromadb(db, batched_chromadb_insertions)

    print(f"Ingestion complete! You can now run the {CUSTOM_NAME} prototype to query your documents")


def add_documents_to_chromadb(db, chromadb_insertion):
    for batched_chromadb_insertion in chromadb_insertion:
        try:
            db.add_documents(batched_chromadb_insertion)
        except ValueError as e:
            print(f"Error: {e}\nSkipping this batch of documents")
            print(batched_chromadb_insertion)
            continue


if __name__ == "__main__":
    main()
