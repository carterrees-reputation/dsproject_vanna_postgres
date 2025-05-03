# dsproject_vanna_postgres

A project demonstrating how to connect Vanna.AI to a local PostgreSQL database for testing and querying.

This project includes scripts for generating synthetic data, setting up a local PostgreSQL database, training a Vanna.AI model on the database schema and data, and running a Vanna.AI Flask application for natural language querying.

## Code Files

The `code/` directory contains the following files:

- `faker_data.py`: Script to generate synthetic data for tenant, location, and review tables using the Faker library.
- `postgres_database_info.sql`: SQL script to retrieve database schema information.
- `postgres_ingest_reviews.sql`: SQL script to ingest the generated review data into the PostgreSQL database.
- `qdrant_vanna_upsert.py`: Script to handle Qdrant collection creation and data upsertion for Vanna.AI.
- `reset_postgres_project.sh`: Shell script to reset the local PostgreSQL database setup.
- `run_vanna_api.py`: Script to run the Vanna.AI Flask application for interacting with the trained model.
- `setup_postgres_project.sh`: Shell script to set up the local PostgreSQL database.
- `vanna_train.py`: Main script to configure and train the Vanna.AI model using the local database and Qdrant.
