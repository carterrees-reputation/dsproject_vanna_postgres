# dsproject_vanna_postgres

A data science project demonstrating how to connect Vanna.AI to a local PostgreSQL database, generate synthetic data, train a Vanna model, and query the database using natural language. The project leverages Qdrant as a vector database and OpenAI for LLM-powered SQL generation. **In addition to synthetic data generated with Faker, this project also includes real location and comment data sourced from our BigQuery database as an example.**

---

## Overview

This project provides a full workflow for:
- Generating synthetic business/location/review data using Faker
- Ingesting both synthetic and real data (from BigQuery) into a local PostgreSQL database
- Setting up Qdrant as a vector store for Vanna
- Training Vanna.AI on your database schema and example queries
- Running a Flask API to ask natural language questions about your data

**The project demonstrates how to combine synthetic data with real-world data (from BigQuery) for more robust analytics and LLM-powered querying.**

---

## Features
- **Synthetic Data Generation**: Uses Faker to create realistic tenants, locations, and comments.
- **Real Data Integration**: Includes example location and comment data exported from our actual BigQuery database.
- **Automated Database Ingestion**: Python scripts to upload both synthetic and real CSVs to Postgres.
- **Qdrant Integration**: Stores embeddings for schema, documentation, and training Q&A pairs.
- **Vanna Training**: Trains on schema, documentation, and custom SQL examples (including joins).
- **Flask API**: Query your data using natural language.
- **Extensible**: Easily add new tables, training examples, or data sources.

---

## Project Structure

```
dsproject_vanna_postgres/
├── code/
│   ├── faker_data.py                  # Generate synthetic data
│   ├── upload_comments_to_postgres.py # Upload comments.csv to Postgres
│   ├── upload_locations_to_postgres.py# Upload locations_exploded_final.csv to Postgres
│   ├── explode_address_final.py       # Explode address JSON in locations
│   ├── vanna_train.py                 # Train Vanna on schema, docs, and Q&A
│   ├── run_vanna_api.py               # Run Flask API for Vanna
│   ├── qdrant_vanna_upsert.py         # Ensure Qdrant collection exists
│   └── ...
├── data/
│   ├── comments.csv                   # Synthetic and/or real comments data
│   ├── locations.csv                  # Raw locations data (synthetic or real)
│   ├── locations_exploded_final.csv   # Locations with exploded address fields
│   └── ...
├── outputs/                           # Output files (if any)
├── .env                               # Environment variables (not committed)
├── .gitignore                         # Excludes data/ and sensitive files
└── README.md                          # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/carterrees-reputation/dsproject_vanna_postgres.git
cd dsproject_vanna_postgres
```

### 2. Install Dependencies
Create and activate a virtual environment, then install requirements:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
(If requirements.txt is missing, install: `psycopg2-binary`, `pandas`, `faker`, `python-dotenv`, `qdrant-client`, `openai`, `flask`)

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_NAME=test_database
DB_USER=carterrees
DB_PASSWORD=yourpassword
DB_PORT=5432
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## Data Generation & Ingestion

1. **Generate Synthetic Data**
   - Run `faker_data.py` to create CSVs for tenants, locations, and comments.

2. **(Optional) Use Real Data from BigQuery**
   - You can also use exported CSVs from your BigQuery `locations` and `comments` tables. Place these files in the `data/` directory and use the provided ingestion scripts to load them into Postgres.

3. **Explode Address Fields**
   - Run `explode_address_final.py` to convert address JSON to columns in `locations_exploded_final.csv`.

4. **Upload Data to Postgres**
   - Run `upload_comments_to_postgres.py` and `upload_locations_to_postgres.py` to load data into the database.

---

## Database Setup

- Create the `test_database` database and the required tables (`comments`, `locations`) using the provided DDL in `vanna_train.py` or via psql.

---

## Training Vanna

- Run the training script:
  ```bash
  python code/vanna_train.py
  ```
- This will:
  - Connect to Postgres and Qdrant
  - Add schema, documentation, and example SQL Q&A pairs (including join queries)
  - Store embeddings in Qdrant

---

## Running the API

- Start the Flask API:
  ```bash
  python code/run_vanna_api.py
  ```
- The API will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)
- You can ask questions via the web UI or by sending POST requests to `/ask`:
  ```bash
  curl -X POST http://127.0.0.1:5000/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "How many comments are there for each location?"}'
  ```

---

## Example Questions
- How many comments are there for each location?
- What is the total number of comments for each tenant?
- How many locations have more than 10 comments?
- What is the average number of comments per location?
- For each tenant, which location had the largest increase in comments between two consecutive months?
- How many unique sentiment values are there and what are their counts?
- What are the location IDs of locations that have more than 10 comments and were added after a specific date?

---

## Troubleshooting
- **Database connection errors:** Ensure Postgres is running and credentials in `.env` are correct.
- **Qdrant errors:** Make sure your Qdrant instance is running and accessible.
- **OpenAI errors:** Check your API key and usage limits.
- **Schema mismatches:** Ensure your CSV columns match your table definitions.
- **Flask app errors:** Check for missing environment variables or port conflicts.

---

## Credits
- [Vanna.AI](https://vanna.ai/)
- [Qdrant](https://qdrant.tech/)
- [OpenAI](https://openai.com/)
- [Faker](https://faker.readthedocs.io/)
- [PostgreSQL](https://www.postgresql.org/)

---

## License
MIT License
