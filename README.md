# Mail/Phone Scraping

This short python script gets a query to search for as a parameter and retrieves all the emails and phone numbers inside the 30 first results


## Requirements

- [Python 3.x](https://www.python.org/downloads/)
- `pip` (Python package installer)

### Libraries

This project requires the following Python libraries (may be outdated, correct list inside `requirements.txt` file):
- `beautifulsoup4`
- `certifi`
- `charset-normalizer`
- `googlesearch-python`
- `idna`
- `requests`
- `soupsieve`
- `urllib3`

These libraries will be installed automatically inside a virtual environment via the `requirements.txt` file.

## Setup

1. **Clone the repository**:
    ```bash
    git clone [https://github.com/yourusername/yourproject.git](https://github.com/filo-g/href-scraper)
    cd href-scraper
    ```

2. **Add exec permissions to both files**:
    ```bash
    chmod +x setup.sh
    chmod +x run.sh
    ```

3. **Run `setup.sh`**:
   This will create the virtual environment and install the requirements
    ```bash
    ./setup.sh
    ```

## Usage

To execute the application with a string parameter, run:

```bash
./run.sh "example string here"
```
