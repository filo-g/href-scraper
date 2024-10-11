import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
import os
import sys

# Function to validate and extract emails from mailto links
def extract_emails_from_href(soup):
    emails = set()
    # Find all <a> tags with href starting with mailto:
    for a in soup.find_all('a', href=re.compile(r'^mailto:')):
        email = a['href'].replace('mailto:', '').strip()
        if email:
            emails.add(email)
    return emails

# Function to scrape emails from the entire page content
def extract_emails_from_page(soup):
    # Regex pattern to match typical email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return set(re.findall(email_pattern, soup))  # Return as a set to ensure unique results

# Function to validate and extract phone numbers from tel links
def extract_phone_numbers_from_href(soup):
    phone_numbers = set()
    # Find all <a> tags with href starting with tel:
    for a in soup.find_all('a', href=re.compile(r'^tel:')):
        phone_number = a['href'].replace('tel:', '').strip()
        if phone_number:
            phone_numbers.add(phone_number)
    return phone_numbers

# Function to scrape phone numbers from the entire page content
def extract_phone_numbers_from_page(soup):
    # Define a set of keywords to look for in class, id, or attributes
    keywords = ['phone', 'number', 'telefono', 'numero']
    
    # Find elements where class, id, or attributes contain any of the keywords as substrings
    phone_elements = soup.find_all(lambda tag: any(
        any(keyword in (attr or '') for attr in (tag.get('class') or []) + [(tag.get('id') or '')] + list(tag.attrs.keys()))
        for keyword in keywords
    ))

    # Additionally, search inside header and footer elements
    header_elements = soup.find_all('header')
    footer_elements = soup.find_all('footer')

    # Combine all the elements (phone, header, and footer)
    relevant_elements = phone_elements + header_elements + footer_elements

    # Initialize an empty set to store found phone numbers
    phone_numbers = set()
    
    # Regex pattern to match phone numbers (e.g., international and local formats)
    phone_pattern = r'\+?\d[\d\s\-()]{7,15}'
    
    # Extract phone numbers from the text of each selected element
    for element in relevant_elements:
        text_content = element.get_text(strip=True)
        numbers_found = re.findall(phone_pattern, text_content)
        phone_numbers.update(numbers_found)
    
    return phone_numbers

# Main function to scrape contact info from a URL
def scrape_contact_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.5',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Ensure the response content is in HTML
        soup = BeautifulSoup(response.content, 'html.parser')  # Use response.content to ensure binary data is handled correctly
        page_content = response.text  # The full HTML content as a string

        # Find all valid emails and phone numbers in the page text
        emails = extract_emails_from_href(soup)
        phone_numbers = extract_phone_numbers_from_href(soup)

        # If no emails found, scrape the entire page for emails
        if not emails:
            emails = extract_emails_from_page(page_content)

        # If no phone numbers found, scrape the entire page for phone numbers
        if not phone_numbers:
            phone_numbers = extract_phone_numbers_from_page(soup)

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

    # Only write to file if there are valid entries
    if results:  # Check if results is not empty
        with open(filepath, 'w') as f:  # Ensure overwrite with 'w' mode
            # Create sets to keep track of unique emails and phone numbers across all results
            all_emails = set()
            all_phones = set()

            for entry in results:
                # Only save unique emails and phone numbers
                unique_emails = set(entry['emails']) - all_emails
                unique_phones = set(entry['phones']) - all_phones
                
                # If there are no new unique emails or phones, skip this entry
                if not unique_emails and not unique_phones:
                    continue

                # Update the global sets with the new unique entries
                all_emails.update(unique_emails)
                all_phones.update(unique_phones)

                f.write(f"Website Name: {entry['name']}\n")
                f.write(f"URL: {entry['url']}\n")
                f.write(f"Emails: {', '.join(unique_emails) if unique_emails else 'None'}\n")
                f.write(f"Phone Numbers: {', '.join(unique_phones) if unique_phones else 'None'}\n")
                f.write("\n" + "-"*50 + "\n\n")

    else:
        print(f"No valid entries found. The file '{filename}' will not be created.")

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