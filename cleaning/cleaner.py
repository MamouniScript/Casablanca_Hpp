import pandas as pd
import re
import os

# Load the CSV file into a DataFrame
file_path = "../data/scraped/16h28_18-10_heavyScraped.csv"  # Replace with your actual file name
df = pd.read_csv(file_path)

# Extract the file name without the extension
file_name = os.path.basename(file_path).split('.')[0]

# Clean the 'price' column (remove text like 'DH' and 'À partir de', keep only numeric values)
df['price'] = df['price'].apply(lambda x: re.sub(r'[^\d]', '', x) if isinstance(x, str) else None)

# Drop rows where 'price' is missing or not a valid number
df = df[df['price'].apply(lambda x: x.isnumeric() if isinstance(x, str) else False)]

# Convert 'price' to numeric format
df['price'] = pd.to_numeric(df['price'])

# Clean 'location' column by stripping unnecessary whitespaces
df['location'] = df['location'].str.strip()

# Extract number of rooms and size in m² from the 'details' column
df['rooms'] = df['details'].apply(lambda x: re.findall(r'(\d+) chambres?', x) if pd.notna(x) and x != "N/A" else None)
df['size_m2'] = df['details'].apply(lambda x: re.findall(r'(\d+) m²', x) if pd.notna(x) and x != "N/A" else None)

# Handle missing values (replace 'N/A' with None)
df.replace('N/A', None, inplace=True)

# Split 'features' into a list
df['features'] = df['features'].apply(lambda x: x.split(', ') if pd.notna(x) else [])

# Save cleaned data to a new CSV file
cleaned_file_path = f"../data/cleaned/cleaned_{file_name}.csv"
df.to_csv(cleaned_file_path, index=False)

print(f"Cleaned data saved to: {cleaned_file_path}")
