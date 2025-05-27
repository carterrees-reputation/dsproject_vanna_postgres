import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

CSV_PATH = 'data/comments.csv'  # Adjust path if needed

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    with open(CSV_PATH, 'r') as f:
        # Use copy_expert for more control (handles headers)
        copy_sql = '''
            COPY comments(tenant_id, entity_id, comment_id, text, created_date, location_updated_date, overall_sentiment_score, text_language, removed)
            FROM STDIN WITH CSV HEADER DELIMITER AS ','
        '''
        cur.copy_expert(sql=copy_sql, file=f)
    conn.commit()
    print(f"Successfully uploaded {CSV_PATH} to the comments table.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error uploading CSV to Postgres: {e}") 