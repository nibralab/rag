import os
from dotenv import load_dotenv
from chromadb.config import Settings

load_dotenv()

# Define the folder for storing database
CUSTOM_NAME = os.environ.get('CUSTOM_DIR', 'demo')
CUSTOM_DIR = os.path.join('prototypes', CUSTOM_NAME)
PERSIST_DIRECTORY = os.environ.get('PERSIST_DIRECTORY', os.path.join(CUSTOM_DIR, 'db'))

# Define the Chroma settings
CHROMA_SETTINGS = Settings(
        persist_directory=PERSIST_DIRECTORY,
        anonymized_telemetry=False
)
