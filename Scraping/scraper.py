import time
import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

# Define the base URLs
first_page_url = "https://www.mubawab.ma/fr/ct/casablanca/immobilier-a-vendre"
base_url = "https://www.mubawab.ma/fr/ct/casablanca/immobilier-a-vendre:p:{}"

# Scrape function to get the listing data from each page
def scrape_page(url):
    headers = {
        "User-Agent": "Your User Agent String"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    listings = soup.find_all("li", class_="listingBox")
    data = []
    for listing in listings:
        price = listing.find("span", class_="priceTag").text.strip() if listing.find("span", class_="priceTag") else "N/A"
        location = listing.find("h3", class_="listingH3").text.strip() if listing.find("h3", class_="listingH3") else "N/A"
        details = listing.find("h4", class_="listingH4").text.strip() if listing.find("h4", class_="listingH4") else "N/A"

        # Append the data to the list
        data.append([price, location, details])
        
        print(f"Price: {price}")
        print(f"Location: {location}")
        print(f"Details: {details}")
        print("-" * 50)
    
    return data

# List to hold all scraped data
all_data = []

# Scrape the first page
print("Scraping the first page...")
data = scrape_page(first_page_url)
all_data.extend(data)

# Loop through all subsequent pages
for page in range(2, 5):  # From page 2 to 4
    print(f"Scraping page {page}")
    url = base_url.format(page)
    data = scrape_page(url)
    all_data.extend(data)
    
    # Sleep for 3-5 minutes between page requests
    # time.sleep(random.uniform(180, 300))  # Uncomment for sleep

# Create the directory if it doesn't exist
directory = "../data/scraped"
os.makedirs(directory, exist_ok=True)

# Get the current datetime for filename
now = datetime.now()
timestamp = now.strftime("%Hh%M_%d-%m")  # Format: HHhMM_DD-MM
filename = os.path.join(directory, f"{timestamp}_scrape.csv")

# Save data to a CSV file
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Price', 'Location', 'Details'])
    writer.writerows(all_data)

print(f"Scraping complete! Data saved to '{filename}'.")
