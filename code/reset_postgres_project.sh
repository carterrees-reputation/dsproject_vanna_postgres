#!/bin/bash

# === Load environment variables from .env ===
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❗ .env file not found. Please create one with DB_USER and DB_PASS."
    exit 1
fi

# === Check required variables ===
if [ -z "$DB_USER" ]; then
    echo "❗ DB_USER must be set in .env"
    exit 1
fi

# === Take database name from CLI argument ===
DB_NAME=$1

if [ -z "$DB_NAME" ]; then
    echo "❗ Usage: $0 <database_name>"
    exit 1
fi

# === Drop the database ===
echo "Dropping database '$DB_NAME' if it exists..."
psql postgres <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
EOF

echo "✅ Done! Database '$DB_NAME' has been dropped."
