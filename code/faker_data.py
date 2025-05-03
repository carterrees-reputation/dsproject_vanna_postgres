import csv
import os
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Define the number of tenants and reviews
num_tenants = 20
reviews_per_tenant = 1000 // num_tenants # Ensure 1000 reviews total
total_reviews = num_tenants * reviews_per_tenant # Total reviews will be 1000

# Generate tenant and location IDs
# Each tenant will have between 1 and 5 locations
tenant_locations = {}
location_counter = 1
for i in range(1, num_tenants + 1):
    tenant_id = i
    num_locations = random.randint(1, 5)
    locations = [location_counter + j for j in range(num_locations)]
    tenant_locations[tenant_id] = locations
    location_counter += num_locations

# Prepare data for CSV
data = []
comment_id_counter = 1

# Generate reviews for each tenant
for tenant_id in range(1, num_tenants + 1):
    locations_for_tenant = tenant_locations[tenant_id]
    for _ in range(reviews_per_tenant):
        comment_id = comment_id_counter
        comment_id_counter += 1

        # Randomly pick a location for this tenant
        location_id = random.choice(locations_for_tenant)

        # Generate comment text with some sentiment variation
        sentiment_type = random.choice(['positive', 'negative', 'neutral'])
        if sentiment_type == 'positive':
            comment = random.choice([
                fake.sentence() + " Great experience!",
                fake.paragraph() + " Highly recommend.",
                "Fantastic service! " + fake.text(max_nb_chars=80),
                "Loved it! " + fake.sentence(nb_words=10),
                fake.sentence() + " Will definitely come back."
            ])
        elif sentiment_type == 'negative':
             comment = random.choice([
                fake.sentence() + " Very disappointing.",
                fake.paragraph() + " Would not recommend.",
                "Terrible experience. " + fake.text(max_nb_chars=80),
                "Didn't like it. " + fake.sentence(nb_words=10),
                fake.sentence() + " Won't be returning."
            ])
        else: # neutral
             comment = random.choice([
                fake.sentence(),
                fake.paragraph(),
                fake.text(max_nb_chars=100),
                fake.sentence(nb_words=15),
            ])

        # Generate a recent created date
        created_date = fake.date_time_between(start_date='-1y', end_date='now')

        data.append([comment_id, tenant_id, location_id, comment, created_date.strftime('%Y-%m-%d %H:%M:%S')])

# Define the absolute output directory path provided by the user
output_dir = '/Users/crees/PycharmProjects/dsproject_vanna_postgres/data' # Use the absolute path

# Define the output filename
output_filename = 'reviews.csv'

# Combine the directory and filename to get the full output path
output_filepath = os.path.join(output_dir, output_filename)

# Ensure the data directory exists
os.makedirs(output_dir, exist_ok=True)

# Write data to CSV
with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)

    # Write header
    csv_writer.writerow(['comment_id', 'tenant_id', 'location_id', 'comment', 'created_date'])

    # Write data rows
    csv_writer.writerows(data)

print(f"Successfully generated {total_reviews} reviews and saved to {output_filepath}")
