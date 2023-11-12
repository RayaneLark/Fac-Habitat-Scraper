# scheduler.py

import time
import schedule
from fach_scraper import scrap_fach_data

def job():
    print("Job started")
    scrap_fach_data()
    print("Job completed")

# Define the job to run every 30 minutes
schedule.every(30).minutes.do(job)

# Infinite loop to run the job
while True:
    schedule.run_pending()
    time.sleep(60)  # Wait for a minute to avoid using too much CPU resources
