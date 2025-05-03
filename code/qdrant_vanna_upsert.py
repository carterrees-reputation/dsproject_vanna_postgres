# code/qdrant_vanna_upsert.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
import os
from qdrant_client.http.exceptions import UnexpectedResponse

# Load environment variables
load_dotenv()

# Load Qdrant URL and API key from .env file
qdrant_url = os.getenv('QDRANT_URL')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

# Check if Qdrant URL is loaded
if not qdrant_url:
    print("Error: QDRANT_URL environment variable not set. Please add it to your .env file.")
    exit(1) # Exit if essential variable is missing

# Check if Qdrant API key is loaded (optional depending on your Qdrant setup, but good practice)
if not qdrant_api_key and "cloud.qdrant.io" in qdrant_url: # Assuming API key is needed for cloud
     print("Error: QDRANT_API_KEY environment variable not set. Please add it to your .env file.")
     exit(1) # Exit if essential variable is missing for cloud


# Initialize Qdrant client
qdrant_client_instance = QdrantClient(
    url=qdrant_url, # Use URL from .env
    api_key=qdrant_api_key,
)

# Define Qdrant collection parameters
collection_name = "vanna_testing"
# Define vector parameters based on typical OpenAI embeddings (size 1536, Cosine distance)
# Using VectorParams class for clarity as recommended by Qdrant docs
vector_params = VectorParams(
    size=1536,
    distance=Distance.COSINE,
)

# --- Collection Creation Logic ---
print(f"Checking for Qdrant collection '{collection_name}'...")
try:
    # Attempt to get collection info to check existence
    qdrant_client_instance.get_collection(collection_name=collection_name)
    print(f"Qdrant collection '{collection_name}' already exists.")
except UnexpectedResponse as e:
    if e.status_code == 404:
         print(f"Qdrant collection '{collection_name}' not found. Creating it...")
         # Create the collection
         qdrant_client_instance.create_collection(
             collection_name=collection_name,
             vectors_config=vector_params # Use the defined vector parameters
         )
         print(f"Qdrant collection '{collection_name}' created.")
    else:
         print(f"An unexpected error occurred checking or creating Qdrant collection: {e}")
         exit(1) # Exit on other Qdrant errors
except Exception as e:
    print(f"An error occurred connecting to Qdrant or checking collection: {e}")
    exit(1) # Exit on any other connection errors

print(f"Qdrant setup script finished. Collection '{collection_name}' is ready.")

# You might want to add logic here to upsert initial data if needed later,
# but for now, it just ensures the collection exists.