# code/run_vanna_api.py
from vanna.openai import OpenAI_Chat
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv, find_dotenv
import os

from vanna.flask import VannaFlaskApp # Import VannaFlaskApp

# --- Manual .env Parsing and DB Environment Variable Setting (Copy from vanna_train.py) ---
# This part is copied from vanna_train.py to ensure DB credentials are set correctly
print("\n--- Debug: Reading .env file content directly and manually parsing DB variables ---")
dotenv_path_direct_read = os.path.join(os.getcwd(), '.env')
db_config = {} # Dictionary to store manually parsed DB config

if os.path.exists(dotenv_path_direct_read):
    try:
        with open(dotenv_path_direct_read, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                print(f"Line {i+1}: {line}")

                # Basic manual parsing for DB variables
                if line.startswith("DB_HOST="):
                    db_config['DB_HOST'] = line.split('=', 1)[1]
                    if db_config['DB_HOST'].startswith('"') and db_config['DB_HOST'].endswith('"'):
                         db_config['DB_HOST'] = db_config['DB_HOST'][1:-1]
                elif line.startswith("DB_NAME="):
                    db_config['DB_NAME'] = line.split('=', 1)[1]
                    # Remove quotes if present
                    if db_config['DB_NAME'].startswith('"') and db_config['DB_NAME'].endswith('"'):
                         db_config['DB_NAME'] = db_config['DB_NAME'][1:-1]
                elif line.startswith("DB_USER="):
                    db_config['DB_USER'] = line.split('=', 1)[1]
                    if db_config['DB_USER'].startswith('"') and db_config['DB_USER'].endswith('"'):
                         db_config['DB_USER'] = db_config['DB_USER'][1:-1]
                elif line.startswith("DB_PASSWORD="):
                    db_config['DB_PASSWORD'] = line.split('=', 1)[1]
                    if db_config['DB_PASSWORD'].startswith('"') and db_config['DB_PASSWORD'].endswith('"'):
                         db_config['DB_PASSWORD'] = db_config['DB_PASSWORD'][1:-1]
                    elif db_config['DB_PASSWORD'].startswith("'") and db_config['DB_PASSWORD'].endswith("'"):
                         db_config['DB_PASSWORD'] = db_config['DB_PASSWORD'][1:-1]


                elif line.startswith("DB_PORT="):
                    port_str = line.split('=', 1)[1]
                    if port_str.startswith('"') and port_str.endswith('"'):
                         port_str = port_str[1:-1]
                    elif port_str.startswith("'") and port_str.endswith("'"):
                         port_str = port_str[1:-1]
                    try:
                        db_config['DB_PORT'] = int(port_str)
                    except ValueError:
                        print(f"Warning: DB_PORT in .env is not a valid integer: '{port_str}'. Will attempt connection without explicit port.")
                        db_config['DB_PORT'] = None


    except Exception as e:
        print(f"Error reading or parsing .env file: {e}")
else:
    print(f".env file not found at {dotenv_path_direct_read}. Manual parsing skipped.")
print("------------------------------------------------------------------")

# --- Set environment variables manually from parsed config ---
print("\n--- Debug: Manually setting DB Environment Variables ---")
for key, value in db_config.items():
    if value is not None:
        os.environ[key] = str(value)
        print(f"Set os.environ['{key}'] to '{os.environ[key]}'")
    else:
         if key == 'DB_PORT':
              if 'DB_PORT' in os.environ:
                   del os.environ['DB_PORT']
              print(f"DB_PORT value was invalid or None, not setting in os.environ.")
print("----------------------------------------------------------")
# --- End manual setting ---

# Now, we still call load_dotenv for other variables
dotenv_path_explicit = find_dotenv(usecwd=True)
if dotenv_path_explicit:
    print(f"\nDebug: Found .env file at: {dotenv_path_explicit}")
    dotenv_loaded = load_dotenv(dotenv_path=dotenv_path_explicit)
    print(f"Debug: load_dotenv() returned: {dotenv_loaded}")
else:
    print("\nDebug: .env file not found by find_dotenv(). load_dotenv() will not be called with explicit path.")
    dotenv_loaded = False

print("\n--- Debug: Environment Variables After load_dotenv (Post-Manual Set) ---")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"QDRANT_URL: {os.getenv('QDRANT_URL')}")
print(f"QDRANT_API_KEY (partial): {os.getenv('QDRANT_API_KEY')[:4]}...")
print(f"OPENAI_API_KEY (partial): {os.getenv('OPENAI_API_KEY')[:4]}...")
print(f"PGHOST: {os.getenv('PGHOST')}")
print(f"PGDATABASE: {os.getenv('PGDATABASE')}")
print(f"PGUSER: {os.getenv('PGUSER')}")
print(f"PGPASSWORD: {os.getenv('PGPASSWORD')}")
print(f"PGPORT: {os.getenv('PGPORT')}")
print("--------------------------------------------------------------------------")


# --- Vanna and Database Setup (Copy from vanna_train.py) ---
# Load Qdrant and OpenAI API keys from env
qdrant_url = os.getenv('QDRANT_URL')
qdrant_api_key = os.getenv('QDRANT_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not qdrant_url or not openai_api_key:
     print("Error: QDRANT_URL or OPENAI_API_KEY environment variables not set.")
     exit(1)

qdrant_client_instance = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
)

collection_name = "vanna_testing"

class MyVanna(Qdrant_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config={
            'client': config['client'],
            'documentation_collection_name': collection_name,
            'ddl_collection_name': collection_name,
            'sql_collection_name': collection_name,
        })
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={
    'client': qdrant_client_instance,
    'api_key': openai_api_key,
    'model': 'gpt-4o-mini',
    'allow_llm_to_see_data': True,
})

print("\n--- Debug: Vanna Instance Configuration ---")
print(vn.get_config())
print("------------------------------------------")

# Load database credentials from environment variables
db_host = os.getenv('DB_HOST')
db_dbname = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port_str_final = os.getenv('DB_PORT')
db_port_final = None
if db_port_str_final is not None:
     try:
          db_port_final = int(db_port_str_final)
     except ValueError:
          pass # Warning printed during manual parse

if not all([db_host, db_dbname, db_user, db_password]):
    print("Error: Database credentials not fully set in environment variables.")
    exit(1)
else:
    try:
        connection_params = {
            'host': db_host,
            'dbname': db_dbname,
            'user': db_user,
            'password': db_password
        }
        if db_port_final is not None:
            connection_params['port'] = db_port_final
        else:
             print("Warning: DB_PORT not set or is not a valid integer. Attempting connection without explicit port.")

        vn.connect_to_postgres(**connection_params)
        print("\nSuccessfully connected to the Postgres database for the Vanna API.")
    except Exception as e:
        print(f"Error connecting to the database for the Vanna API: {e}")
        exit(1)
# --- End Vanna and Database Setup ---


# --- Run the Flask App ---
# This starts the web server. Keep this process running.
try:
    print("\nStarting Vanna Flask App...")
    app = VannaFlaskApp(vn)
    app.run() # This will block, running the web server
except Exception as e:
    print(f"Error running Vanna Flask App: {e}")
