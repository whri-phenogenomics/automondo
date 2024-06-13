import time

import click
import json
import os
import requests
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('retrieve_pmids.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Optional Global Variables
NCBI_KEY = "7c7bd2e8c94b474559a8993a626f9ea64008"  # Set this if you have an API key
ENTREZ_EMAIL = "enockniyonkuru250@gmail.com"  # Set this if you have a registered email

def fetch_and_save_full_texts_json(pmids_list, json_dir_path, max_articles_to_save):
    not_found_count = 0
    found_count = 0
    os.makedirs(json_dir_path, exist_ok=True)
    for pmid in tqdm(pmids_list, desc="Fetching PMIDs", total=len(pmids_list)):
        if found_count >= max_articles_to_save:
            break
        # api_url = f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson?pmids={pmid}"
        api_url = f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/pmc_export/biocxml?pmids={pmid}"

        try_again = True
        while try_again:
            response = requests.get(api_url)
            if response.status_code == 200 and response.text.strip():
                try:
                    data = response.json()
                    if data:
                        filename = f"{pmid}.json"
                        full_path = os.path.join(json_dir_path, filename)
                        with open(full_path, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=4)
                        logger.info(f"Saved full text for PM ID {pmid} in '{full_path}'.")
                        found_count += 1
                    else:
                        not_found_count += 1
                    try_again = False
                except json.JSONDecodeError:
                    logger.info(f"Failed to decode JSON for PM ID {pmid}.")
                    not_found_count += 1
                    try_again = False
            elif response.status_code == 429:
                logger.info(f"Rate limit exceeded for PM ID {pmid}. Waiting 3 seconds before retrying...")
                time.sleep(3)
            else:
                logger.info(f"Failed to fetch full text for PM ID {pmid}: HTTP {response.status_code}")
                not_found_count += 1
                try_again = False
    logger.info(f'Total articles found and saved: {found_count}')
    logger.info(f'Total articles not found: {not_found_count}')
    print(f"Total number of articles found and saved: {found_count} / {found_count + not_found_count} ")

@click.command()
@click.option('-p', '--pmid', required=True, help="PubMed ID to process.")
@click.option('-o', '--output-dir', default='./data/pubtator3_json', help="Directory to save JSON files.")
def main(pmid, output_dir):
    pmids_list = [pmid]
    fetch_and_save_full_texts_json(pmids_list, output_dir, 1)

if __name__ == '__main__':
    main()

"""
python3 src/automondo/pubmed_article_fetcher.py -p <PubMed_ID> -o data/<disease_name>/pubtator3_json

"""