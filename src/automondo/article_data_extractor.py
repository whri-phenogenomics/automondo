import click
import json
import os
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('data_preprocessing.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_article_jsons_to_tsv(json_files_path, no_replaced_tsv_file_path, use_full_text=False):
    output_directory = os.path.dirname(no_replaced_tsv_file_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    text_output_dir = os.path.join(output_directory, "texts")
    os.makedirs(text_output_dir, exist_ok=True)

    json_files = [f for f in os.listdir(json_files_path) if f.endswith(".json")]
    with open(no_replaced_tsv_file_path, 'w', encoding='utf-8') as tsv_file:
        tsv_file.write("PMID\tTitle\tTextFilePath\tMondo_ID\tMondo_Label\n")
        for filename in tqdm(json_files, desc="Processing JSON files"):
            file_path = os.path.join(json_files_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                articles = data['PubTator3'] if 'PubTator3' in data else [data]
                for article in articles:
                    pmid = article['id']
                    title = ""
                    abstract = ""
                    full_text = ""
                    for passage in article['passages']:
                        if passage['infons'].get('type') == 'title':
                            title = passage['text']
                        elif passage['infons'].get('type') == 'abstract':
                            abstract = passage['text']
                        else:
                            full_text += " " + passage['text']

                    text_content = full_text if use_full_text else abstract
                    text_file_path = os.path.join(text_output_dir, f"{pmid}.json")

                    # Save text content in a separate JSON file
                    with open(text_file_path, 'w', encoding='utf-8') as text_file:
                        json.dump({"text": text_content}, text_file)

                    # Write the metadata to the TSV file with the reference to the text file
                    tsv_file.write(f"{pmid}\t{title}\t{text_file_path}\t\t\n")


@click.command()
@click.option('-i', '--json_files_path', required=True, help="Path to the directory containing JSON files.")
@click.option('-n', '--no_replaced_tsv_file_path', required=True,
              help="Path to the output TSV file where no replacement occurred.")
@click.option('--use_full_text', is_flag=True, help="Whether to use the full text instead of the abstract.")
def main(json_files_path, no_replaced_tsv_file_path, use_full_text):
    process_article_jsons_to_tsv(json_files_path, no_replaced_tsv_file_path, use_full_text)


if __name__ == '__main__':
    main()

"""
python3 src/automondo/article_data_extractor.py -i data/<PubMed_ID>/pubtator3_json -n data/<PubMed_ID>/<PubMed_ID>_no_replaced.tsv --use_full_text
"""