# Fac-Habitat Scraper

This Python script scrapes data from the Fac-Habitat website to check the availability of student residences in Île-de-France. It filters the residences managed by Fac-Habitat, 
generates URLs for each residence, checks their availability by analyzing the content of the respective pages and saves the available residences in a JSON file.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3
- Required Python packages: `requests`, `beautifulsoup4`, `json`, `os`

## Usage

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fac-habitat-scraper.git
cd fac-habitat-scraper
```
2.1. To execute the script once, run the script:
```python
python fach_scraper.py
```
2.2. To schedule automatic execution of the script at regular intervals, you can use the provided scheduler.py script. This script uses the schedule library to run the scraping job every 30 minutes.
```python
python scheduler.py
```


