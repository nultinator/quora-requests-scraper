import os
import csv
import requests
import json
import logging
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import concurrent.futures
from dataclasses import dataclass, field, fields, asdict

API_KEY = ""

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    API_KEY = config["api_key"]



def get_scrapeops_url(url, location="us"):
    payload = {
        "api_key": API_KEY,
        "url": url,
        "country": location,
        "wait": 2000
        }
    proxy_url = "https://proxy.scrapeops.io/v1/?" + urlencode(payload)
    return proxy_url


## Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_search_results(keyword, location, retries=3):
    formatted_keyword = keyword.replace(" ", "+")
    url = f"https://www.google.com/search?q={formatted_keyword}%20site%3Aquora.com"
    tries = 0
    success = False
    
    while tries <= retries and not success:
        try:
            scrapeops_proxy_url = get_scrapeops_url(url, location=location)
            response = requests.get(scrapeops_proxy_url)
            logger.info(f"Recieved [{response.status_code}] from: {url}")
            if response.status_code == 200:
                success = True
            
            else:
                raise Exception(f"Failed request, Status Code {response.status_code}")
                
                ## Extract Data

            soup = BeautifulSoup(response.text, "html.parser")            
            div_cards = soup.select("div span")


            for div_card in div_cards:
                name = div_card.find("h3")
                link = div_card.find("a")

                if not name or not link:
                    continue

                result_number += 1
                ranking = result_number

                search_data = {
                    "name": name.text,
                    "url": link.get("href"),
                    "rank": ranking
                }

            logger.info(f"Successfully parsed data from: {url}")
            success = True        
                    
        except Exception as e:
            logger.error(f"An error occurred while processing page {url}: {e}")
            logger.info(f"Retrying request for page: {url}, retries left {retries-tries}")
    if not success:
        raise Exception(f"Max Retries exceeded: {retries}")


if __name__ == "__main__":

    MAX_RETRIES = 3
    MAX_THREADS = 5
    PAGES = 1
    LOCATION = "us"

    logger.info(f"Crawl starting...")

    ## INPUT ---> List of keywords to scrape
    keyword_list = ["learn rust"]
    aggregate_files = []

    ## Job Processes
    for keyword in keyword_list:
        filename = keyword.replace(" ", "-")

        scrape_search_results(keyword, LOCATION, retries=MAX_RETRIES)
                
    logger.info(f"Crawl complete.")
