import argparse
import json
import os
from pathlib import Path
import re

import DataPipeline.general_functions as gf

def extract_page_schema_from_string(page_string: str) -> dict:
    '''
    Extracts a defined schema from the raw text representation of a web page.
    
    Args:
        page_string: A string representing the raw text of a web page. It is expected that this comes form save_response_content_to_file() in general_functions.py .

    Returns:
        return_dict: The schema contained within the HTML <script> tags of the page string.
    '''
    script_start = r'<script id="schema-lifestyle_1-0" class="comp schema-lifestyle mntl-schema-unified" type="application/ld\+json">\['
    script_end = r'\]</script>'
    script_pattern = f'{script_start}(.*){script_end}'
    
    extracted_string = (re.search(script_pattern, page_string, re.DOTALL)).group(1)
    return_dict = json.loads(extracted_string)

    return return_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Serious Eats Pre-Processing")
    parser.add_argument('--output-dir', '-o', type=str, default='./Data/SeriousEats/SiteContentPreProcessed', help="Path to the output directory.")
    parser.add_argument('--raw-content-dir', type=str, default='./Data/SeriousEats/SiteContentRaw', help="Path to the directory containing the raw site files pulled from serious_eats_raw_data-ingest.py")
    
    ## Local file handling
    args = parser.parse_args()
    raw_content_loc = Path(f'{args.raw_content_dir}')
    pre_processed_content_loc = Path(f'{args.output_dir}')
    pre_processed_content_loc.mkdir(parents=True, exist_ok=True)


    ## For each file in the raw data ingest, extract the Schema and save as .json to the output directory
    files_list = []
    type_list = []

    for this_file in os.listdir(raw_content_loc):

        if os.path.isfile(f'{raw_content_loc}/{this_file}') and this_file.endswith('.txt'):
            
            this_file_name = re.sub('.txt', '', this_file)
            files_list.append(this_file_name)
            try:
                this_page_str = gf.read_file_as_str(f'{raw_content_loc}/{this_file}')
                this_page_schema = extract_page_schema_from_string(this_page_str)

                gf.save_dict_to_file(this_page_schema, f'{pre_processed_content_loc}/{this_file_name}')

                this_type = this_page_schema['@type']

            except:
                this_type = [None]
                print(f'Error: {this_file}')

            type_list.append(this_type)

    ## Create and save a summary of each schema type extracted from the above loop.
    ## This includes a list of all file names belonging to each schema type, as well as the total count of files.
    summary_dict = {
        this_type: {'file_count' : 0 , 'files' : []}
        for this_type in set().union(*type_list) # Gets unique strings from a list of lists
    }

    for i in range(len(type_list)):
        for this_type in type_list[i]:
            summary_dict[this_type]['file_count'] += 1
            summary_dict[this_type]['files'].append(files_list[i])

    gf.save_dict_to_file(summary_dict, f'{pre_processed_content_loc}/00_preprocessing_summary')

    exit()