import requests
import time
import urllib3
import csv
import os
import random
from bs4 import BeautifulSoup
from datetime import datetime

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# List of user agents for rotation
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    # Add more user agents if needed
]

# Function to get the main page and extract property listings
def get_property_listings(page_url):
    headers = {'User-Agent': random.choice(user_agents)}  # Randomize User-Agent
    print(f"Requesting URL: {page_url}")  # Debugging: Print the URL being requested
    response = requests.get(page_url, headers=headers, verify=False)  # Disable SSL verification
    if response.status_code != 200:
        print(f"Failed to retrieve data from {page_url} - Status code: {response.status_code}")  # Debugging: Check for errors
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    property_list = []
    
    # Extracting basic info from the main listing page
    listings = soup.find_all("li", class_="listingBox")
    print(f"Found {len(listings)} listings on {page_url}")  # Debugging: Number of listings found

    for listing in listings:
        try:
            price = listing.find("span", class_="priceTag").text.strip() if listing.find("span", class_="priceTag") else "N/A"
            location = listing.find("h3", class_="listingH3").text.strip() if listing.find("h3", class_="listingH3") else "N/A"
            details = listing.find("h4", class_="listingH4").text.strip() if listing.find("h4", class_="listingH4") else "N/A"
            announcement_link = listing.find('a', href=True)['href']

            # Append the collected data
            property_list.append({
                'price': price,
                'location': location,
                'details': details,
                'link': announcement_link,  # Complete URL to the property page
            })
            print(f"Added listing: {price}, {location}, {details}")  # Debugging: Listing details added
        except Exception as e:
            print(f"Error parsing listing: {e}")
            continue

    return property_list

# Function to scrape features from a property detail page
def scrape_property_features(property_url):
    headers = {'User-Agent': random.choice(user_agents)}  # Randomize User-Agent
    print(f"Scraping features from: {property_url}")  # Debugging: Property URL being scraped
    try:
        response = requests.get(property_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve data from {property_url} - Status code: {response.status_code}")  # Debugging
            return {'features': []}

        soup = BeautifulSoup(response.text, 'html.parser')
        features = []

        for feature in soup.find_all('div', class_='adFeature'):
            feature_name = feature.find('span').get_text(strip=True)
            features.append(feature_name)

        return {
            'features': features,
        }
    except Exception as e:
        print(f"Error scraping features from {property_url}: {e}")
        return {'features': []}

# Main function to scrape multiple pages and follow detail links for specific features
def scrape_all_pages(base_url, num_pages):
    all_properties = []

    for page_num in range(1, 2):
        if page_num == 1:
            # First page URL is different
            page_url = base_url
        else:
            # Subsequent page URLs follow this pattern
            page_url = f"{base_url}:p:{page_num}"
        
        print(f"Scraping page: {page_url}")
        
        # Get the property listing with basic info
        property_listings = get_property_listings(page_url)
        
        for property_data in property_listings:
            # Extract features from the announcement page for more detail
            features_data = scrape_property_features(property_data['link'])
            
            # Merge basic info with detailed feature info
            property_data.update(features_data)
            all_properties.append(property_data)
        
        # Sleep between page requests to avoid hitting the server too hard
        time.sleep(random.uniform(10, 20))  # Random sleep between 10-20 seconds

    return all_properties

# Function to save the scraped data into a CSV file
def save_to_csv(data):
    if not data:
        print("No data to save.")  # Debugging: No data case
        return
    
    # Create the directory if it doesn't exist
    directory = "../data/scraped"
    os.makedirs(directory, exist_ok=True)
    
    # Get the current datetime for filename
    now = datetime.now()
    timestamp = now.strftime("%Hh%M_%d-%m")  # Format: HHhMM_DD-MM
    filename = os.path.join(directory, f"{timestamp}_heavyScraped.csv")
    
    # Specify the fieldnames for CSV without the 'link'
    fieldnames = ['price', 'location', 'details', 'features']
    
    # Write the data to a CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        # Prepare data for CSV (flatten features into a string)
        for entry in data:
            entry['features'] = ', '.join(entry.get('features', []))  # Convert list of features to a comma-separated string
            
            # Remove the 'link' field before writing to CSV
            entry.pop('link', None)
        
        writer.writerows(data)
    
    print(f"Data saved to {directory}{filename}")

# Start the scraping process
base_url = 'https://www.mubawab.ma/fr/ct/casablanca/immobilier-a-vendre'
num_pages = 1  # Adjust based on how many pages you want to scrape
scraped_data = scrape_all_pages(base_url, num_pages)

# Save the scraped data into a CSV file
save_to_csv(scraped_data)

# Output the scraped data (optional)
if scraped_data:
    for data in scraped_data:
        print(data)
else:
    print("No data was scraped.")