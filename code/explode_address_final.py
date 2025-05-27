import pandas as pd
import ast

csv_path = 'data/locations_exploded.csv'  # Use your latest file

df = pd.read_csv(csv_path, dtype={'address': str})

def parse_address(addr):
    try:
        if pd.isnull(addr) or addr.strip() == '':
            return {}
        # Use ast.literal_eval to parse the Python dict string
        return ast.literal_eval(addr)
    except Exception as e:
        print(f"Error parsing address: {addr}\n{e}")
        return {}

# Parse and expand the address column
address_df = df['address'].apply(parse_address).apply(pd.Series)

# Combine with the original DataFrame (excluding the original address column)
df_exploded = pd.concat([df.drop(columns=['address']), address_df], axis=1)

# Save the result
df_exploded.to_csv('data/locations_exploded_final.csv', index=False)

print("Exploded CSV saved to data/locations_exploded_final.csv") 