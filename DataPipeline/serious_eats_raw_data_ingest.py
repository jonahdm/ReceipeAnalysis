import argparse
from pathlib import Path
import os

import DataPipeline.general_functions as gf

if __name__ == '__main__':

    ## Parse command line arguments
    parser = argparse.ArgumentParser(description="Serious Eats Raw Data Ingestion")
    parser.add_argument('--output-dir', '-o', type=str, default='./Data/SeriousEats/SiteContentRaw', help="Path to the output directory.")
    parser.add_argument('--sitemap-url', type=str, default='https://www.seriouseats.com/sitemap_1.xml', help="The web location of the Serious Eats sitemap.")
    parser.add_argument('--full-refresh', type=str, default= 'False', help="If False, only pages not already present in the output directory will be pulled.")

    ## Local file handling
    args = parser.parse_args()
    raw_content_loc = Path(f'{args.output_dir}')
    raw_content_loc.mkdir(parents=True, exist_ok=True)

    ## Pull Serious Eats sitemap
    gf.save_response_content_to_file(
        # gf.make_web_request(args.sitemap_url, user_agents[1]),
        gf.make_web_request(args.sitemap_url),
        f'{raw_content_loc}/00_sitemap.xml'
    )
    
    ## Parse the downloaded sitemap
    full_url_list = gf.xml_file_to_dict(f'{raw_content_loc}/00_sitemap.xml')
    url_list = [url['loc'] for url in full_url_list['urlset']['url']]
    url_names_list = [url.split('/')[-1] for url in url_list]

    if args.full_refresh != 'True':
        new_url_list = []
        new_url_names_list = []
        for i in range(len(url_names_list)):
            if not os.path.exists(f'{raw_content_loc}/{url_names_list[i]}.txt'):
                new_url_list.append(url_list[i])
                new_url_names_list.append(url_names_list[i])
        url_list = new_url_list
        new_url_names_list = new_url_names_list

    ## Use parsed sitemap to get other pages
    print('Requesting web pages from Serious Eats')
    request_results = gf.get_many_urls(url_list, raw_content_loc, url_names_list)
    gf.save_dict_to_file(request_results, f'{args.output_dir}/00_site_content_results_summary')

    exit()
    