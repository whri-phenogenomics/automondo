import click
from . import fetch_articles, extract_data, process_with_ontogpt

class AutoMondoRunner:
    def __init__(self, pmid, max_articles_to_save, use_full_text, template):
        self.pmid = pmid
        self.max_articles_to_save = max_articles_to_save
        self.use_full_text = use_full_text
        self.template = template
        self.base_data_path = f"data/{pmid}/"
        self.json_files_dir = self.base_data_path + "pubtator3_json/"
        self.no_replaced_tsv_file_path = self.base_data_path + f"{pmid}_no_replaced.tsv"
        self.ontogpt_yaml_files_dir = self.base_data_path + "ontoGPT_yaml/"

    def run(self):
        print(f"Fetching articles for PubMed ID: {self.pmid}...")
        fetch_articles(
            [self.pmid],
            self.json_files_dir,
            self.max_articles_to_save
        )

        print(f"Extracting data from JSON files to TSV...")
        extract_data(
            self.json_files_dir,
            self.no_replaced_tsv_file_path,
            self.use_full_text
        )

        print(f"Processing articles with OntoGPT...")
        process_with_ontogpt(
            self.no_replaced_tsv_file_path,
            self.ontogpt_yaml_files_dir,
            self.template
        )

        print(f"Processing complete. YAML files are saved in {self.ontogpt_yaml_files_dir}")

@click.command()
@click.option('--pmid', prompt='PubMed ID', help='The PubMed ID of the article to process.')
@click.option('--max_articles_to_save', default=1, help='Maximum number of articles to save.')
@click.option('--use_full_text', is_flag=True, help='Whether to use the full text instead of the abstract.')
@click.option('--template', default='maxo', help='Template to use for OntoGPT extraction.')
def main(pmid, max_articles_to_save, use_full_text, template):
    runner = AutoMondoRunner(pmid, max_articles_to_save, use_full_text, template)
    runner.run()

if __name__ == "__main__":
    main()

"""
python3 src/automondo/main.py --pmid <PubMed_ID> --max_articles_to_save <number> --use_full_text --template maxo
"""