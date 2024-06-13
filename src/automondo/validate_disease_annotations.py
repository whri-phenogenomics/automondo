import click
import json
import os
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('validate_disease_annotations.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_disease_annotations(json_dir_path, output_file):
    no_disease_pmids = []
    json_files = [f for f in os.listdir(json_dir_path) if f.endswith(".json")]

    for filename in tqdm(json_files, desc="Validating JSON files"):
        file_path = os.path.join(json_dir_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            articles = data['PubTator3'] if 'PubTator3' in data else [data]
            has_disease = False

            for article in articles:
                for passage in article['passages']:
                    for annotation in passage.get('annotations', []):
                        if annotation['infons'].get('type') == 'Disease':
                            has_disease = True
                            break
                    if has_disease:
                        break
                if has_disease:
                    break

            if not has_disease:
                pmid = article['id']
                no_disease_pmids.append(pmid)

    with open(output_file, 'w') as out_file:
        for pmid in no_disease_pmids:
            out_file.write(f"{pmid}\n")

    logger.info(f"Total PMIDs without disease annotations: {len(no_disease_pmids)}")
    print(f"Total PMIDs without disease annotations: {len(no_disease_pmids)}")


@click.command()
@click.option('-i', '--json_dir_path', required=True, help="Path to the directory containing JSON files.")
@click.option('-o', '--output_file', default='no_disease_pmids.txt',
              help="File to save PMIDs without disease annotations.")
def main(json_dir_path, output_file):
    check_disease_annotations(json_dir_path, output_file)


if __name__ == '__main__':
    main()
