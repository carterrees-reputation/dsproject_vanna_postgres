#!/bin/bash

# === Load environment variables from .env ===
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❗ .env file not found. Please create one with DB_USER and DB_PASS."
    exit 1
fi

# === Check required environment variables ===
if [ -z "$DB_USER" ] || [ -z "$DB_PASS" ]; then
    echo "❗ DB_USER and DB_PASS must be set in .env"
    exit 1
fi

# === Take database name from CLI argument ===
DB_NAME=$1

if [ -z "$DB_NAME" ]; then
    echo "❗ Usage: $0 <database_name>"
    exit 1
fi

# === Create Postgres Role/User ===
echo "Creating role '$DB_USER'..."
psql postgres <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_roles
      WHERE  rolname = '$DB_USER') THEN

      CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASS';
      ALTER ROLE $DB_USER CREATEDB;
      ALTER ROLE $DB_USER CREATEROLE;
   END IF;
END
\$do\$;
EOF

# === Create Database ===
echo "Creating database '$DB_NAME' owned by '$DB_USER'..."
psql postgres <<EOF
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_database
      WHERE  datname = '$DB_NAME') THEN

      CREATE DATABASE $DB_NAME OWNER $DB_USER;
   END IF;
END
\$do\$;
EOF

# === Grant all privileges ===
echo "Granting all privileges on database '$DB_NAME' to '$DB_USER'..."
psql postgres <<EOF
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "✅ Done! Database '$DB_NAME' is fully set up and owned by '$DB_USER'."
