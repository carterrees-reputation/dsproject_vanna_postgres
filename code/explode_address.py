import pandas as pd
import json
import ast
import re

# Path to your CSV file
csv_path = 'data/locations.csv'

# Read the CSV, making sure not to parse the address column as dict
df = pd.read_csv(csv_path, dtype={'address': str}, quoting=1, engine='python')

def clean_address(addr):
    if pd.isnull(addr):
        return None
    # Remove leading/trailing whitespace and newlines
    addr = addr.strip()
    # Remove newlines and excessive spaces inside the JSON
    addr = re.sub(r'\s+', ' ', addr)
    return addr

# Function to parse the JSON string in the 'address' column
def parse_address(addr):
    try:
        if pd.isnull(addr):
            return {}
        addr = clean_address(addr)
        # Try JSON first
        try:
            return json.loads(addr)
        except Exception:
            # Try literal_eval for Python-style dicts
            return ast.literal_eval(addr)
    except Exception as e:
        print(f"Error parsing address: {addr}\n{e}")
        return {}

# Debug print for raw address values
for i, addr in enumerate(df['address']):
    print(f"Row {i}: {addr}")

# Parse the address column
address_df = df['address'].apply(parse_address).apply(pd.Series)

# Combine the new address columns with the original DataFrame (excluding the original address column)
df_exploded = pd.concat([df.drop(columns=['address']), address_df], axis=1)

# Save the result
df_exploded.to_csv('data/locations_exploded.csv', index=False)

print("Exploded CSV saved to data/locations_exploded.csv") 