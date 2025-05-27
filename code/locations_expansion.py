import pandas as pd
import json

# Path to your CSV file
csv_path = 'data/locations.csv'

# Read the CSV, making sure not to parse the address column as dict
df = pd.read_csv(csv_path, dtype={'address': str})

# Function to parse the JSON string in the 'address' column
def parse_address(addr):
    try:
        # Remove any leading/trailing whitespace and ensure it's a valid JSON string
        return json.loads(addr) if pd.notnull(addr) else {}
    except Exception as e:
        print(f"Error parsing address: {addr}\n{e}")
        return {}

# Parse the address column
address_df = df['address'].apply(parse_address).apply(pd.Series)

# Combine the new address columns with the original DataFrame (excluding the original address column)
df_exploded = pd.concat([df.drop(columns=['address']), address_df], axis=1)

# Save the result
df_exploded.to_csv('data/locations_exploded.csv', index=False)

print("Exploded CSV saved to data/locations_exploded.csv")