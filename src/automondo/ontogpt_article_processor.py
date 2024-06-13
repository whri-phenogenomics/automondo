import click
import csv
import os
import json
import logging
from io import BytesIO
from tqdm import tqdm
from ontogpt.engines.spires_engine import SPIRESEngine
from ontogpt.io.template_loader import get_template_details
from ontogpt.cli import write_extraction

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('ontogpt_article_processor.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_article(pubmed_id: str, text: str, ke: SPIRESEngine, output_dir: str, template: str):
    results = ke.extract_from_text(text=text)
    output = BytesIO()
    output_format = "yaml"
    write_extraction(results=results, template=template, output=output, output_format=output_format,
                     knowledge_engine=ke)
    output_filename = os.path.join(output_dir, f"{pubmed_id}.yaml")
    with open(output_filename, "wb") as output_file:
        output.seek(0)
        output_file.write(output.getvalue())


def process_tsv_file(tsv_file_path: str, ke, output_dir: str, template: str):
    with open(tsv_file_path, 'r', encoding='utf-8') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in tqdm(reader, desc="Processing TSV file"):
            pubmed_id = row['PMID']
            text_file_path = row['TextFilePath']
            with open(text_file_path, 'r', encoding='utf-8') as text_file:
                text_content = json.load(text_file)['text']
                process_article(pubmed_id, text_content, ke, output_dir, template)


@click.command()
@click.option('-t', '--tsv_file_path', required=True, help="Path to the TSV file containing article metadata.")
@click.option('-o', '--output_dir', required=True, help="Path to the output directory for YAML files.")
@click.option('--template', default='maxo', help="Template to use for extraction (default: maxo).")
def main(tsv_file_path, output_dir, template):
    ke = SPIRESEngine(
        template_details=get_template_details(template=template),
        model="gpt-4-0125-preview",
        model_source="openai",
    )
    os.makedirs(output_dir, exist_ok=True)
    process_tsv_file(tsv_file_path, ke, output_dir, template)


if __name__ == '__main__':
    main()

"""
python3 src/automondo/ontogpt_article_processor.py -t data/<disease_name>/<disease_name>_no_replaced.tsv -o data/<disease_name>/ontoGPT_yaml --template maxo

"""
