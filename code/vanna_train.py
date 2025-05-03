from vanna.openai import OpenAI_Chat
from vanna.qdrant import Qdrant_VectorStore
from qdrant_client import QdrantClient
# Import necessary models for vector configuration
from qdrant_client.http.models import Distance, VectorParams
# Import TrainingPlan and TrainingPlanItem
from vanna.types import TrainingPlan, TrainingPlanItem
from dotenv import load_dotenv, find_dotenv
import os
import csv
import os
from faker import Faker
import random
from datetime import datetime, timedelta
from vanna.flask import VannaFlaskApp
import traceback # Import traceback

# --- Add code to read .env file content directly and manually parse DB variables ---
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
                    # Keep quotes for password during parsing, or handle escape characters if needed
                    db_config['DB_PASSWORD'] = line.split('=', 1)[1]
                     # If password is quoted, keep the quotes for the value passed to connect_to_postgres
                     # Or, more safely, remove quotes and let the connector handle the raw string
                    if db_config['DB_PASSWORD'].startswith('"') and db_config['DB_PASSWORD'].endswith('"'):
                         db_config['DB_PASSWORD'] = db_config['DB_PASSWORD'][1:-1] # Remove quotes
                    elif db_config['DB_PASSWORD'].startswith("'") and db_config['DB_PASSWORD'].endswith("'"):
                         db_config['DB_PASSWORD'] = db_config['DB_PASSWORD'][1:-1] # Remove quotes


                elif line.startswith("DB_PORT="):
                    port_str = line.split('=', 1)[1]
                    # Remove quotes if present
                    if port_str.startswith('"') and port_str.endswith('"'):
                         port_str = port_str[1:-1]
                    elif port_str.startswith("'") and port_str.endswith("'"):
                         port_str = port_str[1:-1]
                    try:
                        db_config['DB_PORT'] = int(port_str)
                    except ValueError:
                        print(f"Warning: DB_PORT in .env is not a valid integer: '{port_str}'. Will attempt connection without explicit port.")
                        db_config['DB_PORT'] = None # Set to None if not a valid integer


    except Exception as e:
        print(f"Error reading or parsing .env file: {e}")
else:
    print(f".env file not found at {dotenv_path_direct_read}. Manual parsing skipped.")
print("------------------------------------------------------------------")

# --- Set environment variables manually from parsed config ---
print("\n--- Debug: Manually setting DB Environment Variables ---")
for key, value in db_config.items():
    if value is not None:
        os.environ[key] = str(value) # Set in os.environ
        print(f"Set os.environ['{key}'] to '{os.environ[key]}'")
    else:
         # If port was not a valid integer, ensure it's not set
         if key == 'DB_PORT':
              if 'DB_PORT' in os.environ:
                   del os.environ['DB_PORT']
              print("DB_PORT value was invalid or None, not setting in os.environ.")

print("----------------------------------------------------------")
# --- End manual setting ---


# Now, we still call load_dotenv for other variables, but the DB ones are handled manually.
# Using find_dotenv() to locate the nearest .env file in parent directories
dotenv_path_explicit = find_dotenv(usecwd=True) # Start searching from the current working directory
if dotenv_path_explicit:
    print(f"\nDebug: Found .env file at: {dotenv_path_explicit}")
    # Load dotenv, but our manual parsing for DB variables should take precedence
    dotenv_loaded = load_dotenv(dotenv_path=dotenv_path_explicit)
    print(f"Debug: load_dotenv() returned: {dotenv_loaded}")
else:
    print("\nDebug: .env file not found by find_dotenv(). load_dotenv() will not be called with explicit path.")
    dotenv_loaded = False # Indicate that no file was explicitly loaded


# --- Debug: Environment Variables After load_dotenv (Post-Manual Set) ---
print("\n--- Debug: Environment Variables After load_dotenv (Post-Manual Set) ---")
# Print specific DB variables - should match our manual set values now
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"QDRANT_URL: {os.getenv('QDRANT_URL')}") # Add Qdrant env vars to this debug section
print(f"QDRANT_API_KEY (partial): {os.getenv('QDRANT_API_KEY')[:4]}...") # Print partial API key for confirmation
print(f"OPENAI_API_KEY (partial): {os.getenv('OPENAI_API_KEY')[:4]}...") # Print partial API key for confirmation
print(f"PGHOST: {os.getenv('PGHOST')}")
print(f"PGDATABASE: {os.getenv('PGDATABASE')}")
print(f"PGUSER: {os.getenv('PGUSER')}")
print(f"PGPASSWORD: {os.getenv('PGPASSWORD')}")
print(f"PGPORT: {os.getenv('PGPORT')}")
print("--------------------------------------------------------------------------")
# --- End Debug Prints ---


# Load Qdrant URL and API key from env - These should now be correctly set by manual parsing or load_dotenv
qdrant_url = os.getenv('QDRANT_URL')
qdrant_api_key = os.getenv('QDRANT_API_KEY')

if not qdrant_url:
    print("Error: QDRANT_URL environment variable not set. Please add it to your .env file and run qdrant_vanna_upsert.py first.")
    exit(1)

# Load OpenAI API key from env - This should now be correctly set by manual parsing or load_dotenv
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
     print("Error: OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
     exit(1) # Added exit here as well

# Initialize Qdrant client instance that Vanna will use
qdrant_client_instance = QdrantClient(
    url=qdrant_url, # Use URL from env
    api_key=qdrant_api_key,
)

# Define separate Qdrant collection names for different data types
documentation_collection_name = "vanna_documentation"
ddl_collection_name = "vanna_ddl"
sql_collection_name = "vanna_sql"

# --- Add code to delete and recreate the collections with correct dimensions (default vector) ---
print(f"\nAttempting to delete existing Qdrant collections if they exist...")
try:
    qdrant_client_instance.delete_collection(collection_name=documentation_collection_name)
    print(f"Collection '{documentation_collection_name}' deleted.")
except Exception as e:
    print(f"Collection '{documentation_collection_name}' did not exist or could not be deleted: {e}")

try:
    qdrant_client_instance.delete_collection(collection_name=ddl_collection_name)
    print(f"Collection '{ddl_collection_name}' deleted.")
except Exception as e:
    print(f"Collection '{ddl_collection_name}' did not exist or could not be deleted: {e}")

try:
    qdrant_client_instance.delete_collection(collection_name=sql_collection_name)
    print(f"Collection '{sql_collection_name}' deleted.")
except Exception as e:
    print(f"Collection '{sql_collection_name}' did not exist or could not be deleted: {e}")


print(f"Attempting to recreate Qdrant collections with 384 dimensions (default vector)...")
try:
    qdrant_client_instance.recreate_collection(
        collection_name=documentation_collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Collection '{documentation_collection_name}' recreated successfully with 384 dimensions.")
except Exception as e:
    print(f"Error recreating collection '{documentation_collection_name}': {e}")
    exit(1) # Exit if collection recreation fails

try:
    qdrant_client_instance.recreate_collection(
        collection_name=ddl_collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Collection '{ddl_collection_name}' recreated successfully with 384 dimensions.")
except Exception as e:
    print(f"Error recreating collection '{ddl_collection_name}': {e}")
    exit(1) # Exit if collection recreation fails

try:
    qdrant_client_instance.recreate_collection(
        collection_name=sql_collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Collection '{sql_collection_name}' recreated successfully with 384 dimensions.")
except Exception as e:
    print(f"Error recreating collection '{sql_collection_name}': {e}")
    exit(1) # Exit if collection recreation fails

# --- End add code to delete and recreate collection ---


class MyVanna(Qdrant_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config={
            'client': config['client'],
            # Use separate collection names for each data type
            'documentation_collection_name': documentation_collection_name,
            'ddl_collection_name': ddl_collection_name,
            'sql_collection_name': sql_collection_name,
            # Pass embedding config here so Qdrant_VectorStore knows the dimensions for collection creation
            # Note: With explicit recreation above, this might be redundant for creation, but good practice
            'embedding_dimensions': config.get('embedding_dimensions', 384),
            'distance': config.get('distance', Distance.COSINE), # Default distance
        })
        OpenAI_Chat.__init__(self, config=config)

    # Add this method to override the default behavior
    def generate_rewritten_question(self, last_question: str, new_question: str, **kwargs) -> str:
        return new_question

# Prepare the configuration dictionary
vanna_config = {
    'client': qdrant_client_instance,
    'api_key': openai_api_key,
    'model': 'gpt-4o-mini',
    'embedding_model': 'text-embedding-3-small', # Ensure this matches the model that outputs 384 dim
    'embedding_dimensions': 384, # This matches the expected dimension of the collections we want to use
    'allow_llm_to_see_data': True,
    'distance': Distance.COSINE, # Add distance to the main config
}

# --- Add debug print for the config dictionary ---
print("\n--- Debug: Vanna Configuration Dictionary Before Initialization ---")
print(vanna_config)
print("-------------------------------------------------------------------")
# --- End debug print ---

# Initialize MyVanna with the prepared config
vn = MyVanna(config=vanna_config) # Pass the config dictionary

# Load database credentials from environment variables using os.getenv
# These should now be correctly set by our manual parsing
db_host = os.getenv('DB_HOST')
db_dbname = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
# Get port as string and attempt conversion again, but it should be set correctly by manual parsing
db_port_str_final = os.getenv('DB_PORT')
db_port_final = None
if db_port_str_final is not None:
     try:
          db_port_final = int(db_port_str_final)
     except ValueError:
          print(f"Warning: Final DB_PORT value is not a valid integer: '{db_port_str_final}'. Attempting connection without explicit port.")


# Connect to Postgres using credentials from environment variables (now manually set)
# Added checks for database credentials
if not all([db_host, db_dbname, db_user, db_password]):
    print("Error: Database credentials (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD) not fully set in environment variables.")
    exit(1) # Exit if essential credentials are missing
else:
    try:
        connection_params = {
            'host': db_host,
            'dbname': db_dbname,
            'user': db_user,
            'password': db_password
        }
        # Only add port if it was successfully converted to an integer and is not None
        if db_port_final is not None:
            connection_params['port'] = db_port_final
        else:
             print("Warning: DB_PORT not set or is not a valid integer. Attempting connection without explicit port.")


        vn.connect_to_postgres(**connection_params)
        print("Successfully connected to the Postgres database.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        print("Please ensure your database is running and the connection details are correct.")
        print("Also, verify that DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, and DB_PORT environment variables are correctly set.")
        exit(1) # Exit after a connection error

# Proceed directly to training try block if connection was successful (indicated by no exit above)
try:
    print("\nAttempting to fetch information schema and train...")
    df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
    print("Successfully fetched information schema.")

    # --- Debug print for information schema DataFrame ---
    print("\n--- Debug: Information Schema DataFrame Content (First 5 rows) ---")
    if not df_information_schema.empty:
        print(df_information_schema.head().to_markdown(index=False))
    else:
        print("Information schema DataFrame is empty.")
    print("\n--- Debug: Information Schema DataFrame Columns ---")
    print(df_information_schema.columns.tolist())
    print("-------------------------------------------------------------------")
    # --- End debug print ---


    print("Generating training plan...")
    plan = vn.get_training_plan_generic(df_information_schema)
    print("Training plan generated.")
    print("\n--- Training Plan Content (Plan includes all data types) ---")
    if plan and plan._plan:
        print(plan)
    else:
        print("Training plan is empty.")
    print("-----------------------------")

    # --- Explicitly add training data using specific methods (from plan) ---
    print("\n--- Debug: Starting Explicit Training (from plan) ---")
    if plan and plan._plan:
        for item in plan._plan:
            try:
                if item.item_type == TrainingPlanItem.ITEM_TYPE_DDL:
                    print(f"Adding DDL (from plan): {item.item_value[:50]}...")
                    vn.add_ddl(item.item_value)
                    print("DDL added from plan.")
                elif item.item_type == TrainingPlanItem.ITEM_TYPE_IS:
                    print(f"Adding Documentation (Schema): {item.item_value[:50]}...")
                    vn.add_documentation(item.item_value)
                    print("Documentation added.")
                elif item.item_type == TrainingPlanItem.ITEM_TYPE_SQL:
                     # Assuming SQL items in plan already have question and sql in item_name/item_value
                    print(f"Adding SQL Example (from plan): Question='{item.item_name[:50]}...', SQL='{item.item_value[:50]}...'")
                    vn.add_question_sql(question=item.item_name, sql=item.item_value)
                    print("SQL example added from plan.")

            except Exception as e:
                print(f"Error adding training item (Type: {item.item_type if 'item' in locals() else 'unknown'}, Name: {item.item_name if 'item' in locals() else 'unknown'}): {e}") # Added safety for debug print
                import traceback
                traceback.print_exc()
        print("--- Debug: Finished Explicit Training (from plan) ---")
    else:
        print("Skipping explicit training from plan because the plan is empty or invalid.")

    # --- Add explicit DDL training for your specific tables ---
    print("\n--- Debug: Starting Explicit DDL Training for User Tables ---")
    try:
        # Use the actual CREATE TABLE statement for your reviews table, which contains location_id
        actual_reviews_ddl = """
                           Table "public.reviews"
    Column    |            Type             | Collation | Nullable | Default
--------------+-----------------------------+-----------+----------+---------
 comment_id   | integer                     |           | not null |
 tenant_id    | integer                     |           |          |
 location_id  | integer                     |           |          |
 comment      | text                        |           |          |
 created_date | timestamp without time zone |           |          |
Indexes:
    "reviews_pkey" PRIMARY KEY, btree (comment_id)
        """
        print("Adding actual DDL for 'reviews' table (containing location_id)...")
        vn.add_ddl(actual_reviews_ddl)
        print("Actual DDL for 'reviews' table added.")

        # Remove the placeholder DDL for a separate locations table

    except Exception as e:
        print(f"Error during Explicit DDL Training: {e}")
        import traceback
        traceback.print_exc()
    print("--- Debug: Finished Explicit DDL Training for User Tables ---")

    # --- Add explicit Custom Documentation Training ---
    print("\n--- Debug: Starting Explicit Custom Documentation Training ---")
    try:
        # Add your custom documentation strings here
        vn.add_documentation("The reviews table contains customer feedback on locations.")
        vn.add_documentation("Each location_id represents a unique physical location.")
        vn.add_documentation("The tenant_id links reviews to specific tenants or businesses.")
        vn.add_documentation("The comment column contains the text of the customer review.")
        vn.add_documentation("The created_date indicates when the review was submitted.")

        # Added documentation for requested clarifications
        vn.add_documentation("A tenant in the system represents a company or business.")
        vn.add_documentation("Each location is associated with and belongs to a specific tenant.")
        vn.add_documentation("The data in the reviews table is structured such that each row represents a unique comment for a specific location and tenant.")
        print("Custom documentation added.")
    except Exception as e:
        print(f"Error during Explicit Custom Documentation Training: {e}")
        import traceback
        traceback.print_exc()
    print("--- Debug: Finished Explicit Custom Documentation Training ---")


    # --- Check points after explicit training (from plan and manual DDL) ---
    # Remove the manual point checks that caused the AttributeError
    # The script's default output will show the point counts.


    # --- Uncomment the individual training examples if you want to add specific manual data ---
    # DDL example (already added if in plan, but can add more manually)
    # print("\nTraining with additional DDL example...")
    # try:
    #     vn.add_ddl(ddl="""CREATE TABLE other_table (id INT);""")
    #     print("Additional DDL training complete.")
    # except Exception as e:
    #      print(f"Error during additional DDL training: {e}")

    # Documentation example (already added if in plan, but can add more manually)
    # print("\nTraining with additional documentation example...")
    # try:
    #     vn.add_documentation("The other_table stores temporary data.")
    #     print("Additional Documentation training complete.")
    # except Exception as e:
    #      print(f"Error during additional documentation training: {e}")

    # SQL example (uncomment and modify to add specific Q&A pairs)
    print("\nTraining with SQL example...") # Uncomment this to add a specific Q&A pair
    try:
        sql_example = "SELECT COUNT(*) FROM reviews"
        question_for_sql_example = "How many reviews are there?"
        vn.add_question_sql(question=question_for_sql_example, sql=sql_example)
        print("SQL example training complete.")
    except Exception as e:
         print(f"Error during SQL training: {e}")
         import traceback
         traceback.print_exc()

    # At any time you can inspect what training data the package is able to reference
    # ...


    ## Asking the AI
    # This section is for testing a single question during development/debugging of training.
    # For interactive questioning, use the API script (run_vanna_api.py) and curl.
    print("\n--- Asking Vanna (One-time test from training script) ---")
    # Using a question that should now be answerable with the trained schema and SQL example
    question = "how many different locations are there?" # Test with a question that needs schema
    # question = "How many reviews are there?" # Test with the question from the SQL example
    print(f"Question: '{question}'")
    try:
        # --- Debug print before vn.ask ---
        print("--- Debug: Calling vn.ask ---")
        # --- End debug print ---
        # Keep allow_llm_to_see_data=True for the ask call in the script too
        sql_query, results, fig = vn.ask(question=question, allow_llm_to_see_data=True, print_results=False) # Set print_results to False to control output here
        # --- Debug print after vn.ask ---
        print("--- Debug: Returned from vn.ask ---")
        # --- End debug print ---

        print("\nGenerated SQL:")
        print(sql_query)

        if results is not None:
            print("\nResults:")
            print(results)

        if fig is not None:
             print("\nPlotly Figure Generated.")
             # You might want to save the figure to a file here if needed, as fig.show() won't work in a non-interactive terminal
             # fig.write_image("figure.png")


    except Exception as e:
         print(f"Error asking Vanna: {e}")
         import traceback
         traceback.print_exc() # Print full traceback for ask errors


    # --- Add check for total points in Qdrant collections (after all training examples) ---
    # The script's default output will show the total point count.


except Exception as e:
    print(f"\nError during Vanna process: {e}")
    import traceback
    traceback.print_exc()

# --- Run the Flask App ---
# This starts the web server. Keep this process running.
try:
    print("\nStarting Vanna Flask App...")
    # Ensure allow_llm_to_see_data is passed here from the config if needed by the Flask app initialization
    # The Flask app takes the 'vn' instance, which already has the setting in its config.
    app = VannaFlaskApp(vn, allow_llm_to_see_data=True) # Initialize app with the configured vn instance

    # To work around the KeyError in generate_questions and generate_sql within the Flask app,
    # we need to modify the Flask app routes directly or find a way to disable them.
    # Since directly modifying the installed vanna.flask.__init__.py is necessary,
    # and we can't do that directly here, let's try to work around it by:
    # 1. Commenting out the generate_questions route in the Flask app if possible without direct file modification (unlikely).
    # 2. Acknowledge the KeyError in the Flask app's generate_questions/generate_sql
    #    and suggest manually fixing the vanna.flask library code.
    # Let's assume for now we'll hit the KeyError in the app and guide the user.

    app.run() # This will block, running the web server
except Exception as e:
    print(f"Error running Vanna Flask App: {e}")
    import traceback
    traceback.print_exc()