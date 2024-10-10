import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
import os
import sys

# Function to validate and extract emails from mailto links
def extract_emails(soup):
    emails = set()
    # Find all <a> tags with href starting with mailto:
    for a in soup.find_all('a', href=re.compile(r'^mailto:')):
        email = a['href'].replace('mailto:', '').strip()
        if email:
            emails.add(email)
    return emails

# Function to validate and extract phone numbers from tel links
def extract_phone_numbers(soup):
    phone_numbers = set()
    # Find all <a> tags with href starting with tel:
    for a in soup.find_all('a', href=re.compile(r'^tel:')):
        phone_number = a['href'].replace('tel:', '').strip()
        if phone_number:
            phone_numbers.add(phone_number)
    return phone_numbers

# Main function to scrape contact info from a URL
def scrape_contact_info(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.5',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Ensure the response content is in HTML
        soup = BeautifulSoup(response.content, 'html.parser')  # Use response.content to ensure binary data is handled correctly

        # Find all valid emails and phone numbers in the page text
        emails = extract_emails(soup)
        phone_numbers = extract_phone_numbers(soup)

        return emails, phone_numbers
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return set(), set()

# Function to create the output directory if it doesn't exist
def create_output_directory(directory='output'):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to sanitize query for use in a filename
def sanitize_filename(query):
    # Replace spaces with underscores and remove special characters except alphanumeric and underscores
    sanitized = re.sub(r'[^\w\s-]', '', query)  # Remove special characters
    sanitized = sanitized.replace(' ', '_')     # Replace spaces with underscores
    return sanitized

# Function to save the results to a text file (in overwrite mode)
# Function to save the results to a text file (in overwrite mode)
def save_to_file(results, filename):
    output_directory = 'output'
    create_output_directory(output_directory)  # Ensure the output directory exists
    
    # Create the full file path
    filepath = os.path.join(output_directory, filename)
    
    # Check for existing files and add a suffix if necessary
    base_filename, file_extension = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base_filename}_{counter}{file_extension}"
        counter += 1
    
    with open(filepath, 'w') as f:  # Ensure overwrite with 'w' mode
        for entry in results:
            f.write(f"Website Name: {entry['name']}\n")
            f.write(f"URL: {entry['url']}\n")
            f.write(f"Emails: {', '.join(entry['emails']) if entry['emails'] else 'None'}\n")
            f.write(f"Phone Numbers: {', '.join(entry['phones']) if entry['phones'] else 'None'}\n")
            f.write("\n" + "-"*50 + "\n\n")

# Main script
def main():
    # Check if the search query is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python app.py \"search query\"")
        sys.exit(1)  # Exit the program with an error code

    # Get the search query from the command-line argument
    query = sys.argv[1].strip()
    
    # Sanitize query to use it as part of the filename
    sanitized_query = sanitize_filename(query)
    filename = f"{sanitized_query}.txt"
    
    num_results = 30
    results = []

    # Perform Google search to get URLs
    search_results = search(query, num_results=num_results, lang="es")
    
    for url in search_results:
        print(f"Scraping {url}")
        emails, phone_numbers = scrape_contact_info(url)
        
        # Only add entries that have at least one email or phone number
        if emails or phone_numbers:
            results.append({
                'name': url.split('//')[-1].split('/')[0],  # Extract domain name
                'url': url,
                'emails': emails,
                'phones': phone_numbers
            })
    
    # Save the results to a file using the sanitized filename
    save_to_file(results, filename)

    # Additional message if no entries were valid
    if not results:
        print("No valid entries were found. The output file was not created.")

if __name__ == "__main__":
    main()