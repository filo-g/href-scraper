import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search

# Function to validate and extract emails using regex
def extract_valid_emails(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    emails = set(re.findall(email_pattern, text))
    return emails

# Function to validate and clean phone numbers (more relaxed cleaning)
def extract_valid_phone_numbers(text):
    phone_numbers = set()
    # Updated regex to capture phone number patterns (with more flexibility)
    phone_pattern = re.compile(r'(\+?\d{1,4}[\s\-]?)?(?:\(?\d{1,3}?\)?[\s\-]?)?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9}')
    
    for match in re.findall(phone_pattern, text):
        cleaned_number = re.sub(r'[^\d\+\-\(\)\s]', '', match)
        digits_count = re.sub(r'[^\d]', '', cleaned_number)  # Remove non-digits for digit count
        if len(digits_count) >= 10:
            phone_numbers.add(cleaned_number.strip())
    
    return phone_numbers

# Main function to scrape contact info from a URL
def scrape_contact_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all text content from the page
        page_text = soup.get_text(separator=' ')
        
        # Find all valid emails and phone numbers in the page text
        emails = extract_valid_emails(page_text)
        phone_numbers = extract_valid_phone_numbers(page_text)
        
        return emails, phone_numbers
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return set(), set()

# Function to sanitize query for use in a filename
def sanitize_filename(query):
    # Replace spaces with underscores and remove special characters except alphanumeric and underscores
    sanitized = re.sub(r'[^\w\s-]', '', query)  # Remove special characters
    sanitized = sanitized.replace(' ', '_')     # Replace spaces with underscores
    return sanitized

# Function to save the results to a text file (in overwrite mode)
def save_to_file(results, filename):
    with open(filename, 'w') as f:  # Ensure overwrite with 'w' mode
        for entry in results:
            f.write(f"Website Name: {entry['name']}\n")
            f.write(f"URL: {entry['url']}\n")
            f.write(f"Emails: {', '.join(entry['emails']) if entry['emails'] else 'None'}\n")
            f.write(f"Phone Numbers: {', '.join(entry['phones']) if entry['phones'] else 'None'}\n")
            f.write("\n" + "-"*50 + "\n\n")

# Main script
def main():
    # Ask the user for a search query
    query = input("Enter your search query: ").strip()
    
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
        results.append({
            'name': url.split('//')[-1].split('/')[0],  # Extract domain name
            'url': url,
            'emails': emails,
            'phones': phone_numbers
        })
    
    # Save the results to a file using the sanitized filename
    save_to_file(results, filename)
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()