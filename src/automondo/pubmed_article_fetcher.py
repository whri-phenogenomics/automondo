import time

import click
import json
import os
import requests
import logging
from tqdm import tqdm
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('retrieve_pmids.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def fetch_and_save_full_texts_json(pmids_list, json_dir_path, max_articles_to_save):
    not_found_count = 0
    found_count = 0
    os.makedirs(json_dir_path, exist_ok=True)
    existing_pmids = [f.split('.')[0] for f in os.listdir(json_dir_path) if f.endswith('.json')]

    for pmid in tqdm(pmids_list, desc="Fetching PMIDs", total=len(pmids_list)):
        if pmid in existing_pmids:
            logger.info(f"PMID {pmid} already exists in the directory. Skipping...")
            continue
        if found_count >= max_articles_to_save:
            break
        api_url = f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocjson?pmids={pmid}"

        try_again = True
        while try_again:
            response = requests.get(api_url)
            logger.info(f"Fetching PMID {pmid}: HTTP {response.status_code}")
            if response.status_code == 200 and response.text.strip():
                try:
                    data = response.json()
                    if data:
                        logger.info(f"Received data for PMID {pmid}: {data}")
                        filename = f"{pmid}.json"
                        full_path = os.path.join(json_dir_path, filename)
                        with open(full_path, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=4)
                        logger.info(f"Saved full text for PM ID {pmid} in '{full_path}'.")
                        found_count += 1
                    else:
                        logger.info(f"No content for PM ID {pmid}.")
                        not_found_count += 1
                    try_again = False
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON for PM ID {pmid}: {e}")
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
    print(f"Total number of articles found and saved: {found_count} / {found_count + not_found_count}")

def read_pmids_from_xlsx(file_path, column_index=1):
    df = pd.read_excel(file_path, dtype=str) # read as str to avoid .o at end of numbers
    return df.iloc[:, column_index].dropna().str.strip().tolist()

@click.command()
@click.option('-f', '--file_path', default='data/PMID.xlsx', help="Path to the file containing PMIDs.")
@click.option('-o', '--output-dir', default='./data/pubtator3_json', help="Directory to save JSON files.")
@click.option('-m', '--max_articles_to_save', default=100, help="Maximum number of articles to save.")
def main(file_path, output_dir, max_articles_to_save):
    pmids_list = read_pmids_from_xlsx(file_path=file_path)
    fetch_and_save_full_texts_json(pmids_list, output_dir, 200)

if __name__ == '__main__':
    main()

"""
python3 src/automondo/pubmed_article_fetcher.py -f src/resources/PMID_100KGP.xlsx -o data/pubtator3_json -m 200   
"""