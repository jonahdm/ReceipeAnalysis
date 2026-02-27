import argparse
import json
import os
from pathlib import Path
import pandas as pd
import re

import DataPipeline.general_functions as gf

def build_page_summary_dict(pre_processing_summary_dict: dict, as_of: float) -> dict:
    '''
    Pulls data from the pre-processing summary into simple definitions suitable for use in dashboarding.
    
    Args:
        pre_processing_summary_dict: A dictionary file representing the summmary created by serious_eats_data_pre_processing.py .
        as_of: The epoch time of when data was last pulled. 

    Returns:
        return_dict: A dict containing the file count of Articles, Profiles, and Recipes on SeriousEats.
    '''

    ## Combine Article and NewsArticle category into one list of unique pages
    unique_articles = pre_processing_summary_dict['Article']['files']
    unique_articles.extend(pre_processing_summary_dict['NewsArticle']['files'])
    unique_articles = list(set(unique_articles))

    return_dict = {
        'Articles': len(unique_articles),
        'Profiles': pre_processing_summary_dict['ProfilePage']['file_count'],
        'Recipes': pre_processing_summary_dict['Recipe']['file_count'],
        'AsOf': as_of
    }
    
    return return_dict

def count_common_ingredients(ingredients_list: list[dict]) -> list[dict]:
    '''
    Calculates a rough estimate for total amounts of ingredients needed for a list of ingredient dictionaries. Amounts are set to a stnadard speciifed unit (either g or mL).
    
    Args:
        ingredients_list: A list of 'recipeIngredient' dicts, presumably obtained from serious_eats_recipe_processing.py .

    Returns:
        return_list: A list of dicts dict containing the sum total amount and unit of ingredients specified in the function. Intended to be written converted to a pd.DataFrame and writetn to .csv.
    '''

    ## This dict defines what ingredients will be searched for. These ingredients were chosen somewhat arbitrarily.
    ingredients_dict = {
        ## General pattern for each ingredient: 
        ##  'pattern': should be semi-strict and capture the whole ingredient word (ie 'salt' but not 'salted' or 'unsalted')
        ##  'amounts': empty placeholder, 'pref_unit': 'g' or 'mL', 'conversion_ratio': a low-estimate conversion g to mL or vise-versa
        'salt': {'pattern': r'(\bsalt\b)', 'amounts': [], 'pref_unit': 'g', 'conversion_ratio': 0.55},
        'pepper': {'pattern': r'(\bpepper\b)', 'amounts': [], 'units': [], 'pref_unit': 'g', 'conversion_ratio': 0.4},
        'olive_oil': {'pattern': r'(\bolive\b)(?:.+?)(\boil\b)', 'amounts': [], 'units': [], 'pref_unit': 'g', 'conversion_ratio': 0.915},
        'butter': {'pattern': r'(\bbutter\b)', 'amounts': [], 'units': [], 'pref_unit': 'g', 'conversion_ratio': 0.959},
        'flour': {'pattern': r'(\bflour\b)', 'amounts': [], 'units': [], 'pref_unit': 'g', 'conversion_ratio': 0.53},
        'sugar': {'pattern': r'(\bsugar\b)', 'amounts': [], 'units': [], 'pref_unit': 'g', 'conversion_ratio': 0.7}
    }

    ## For each ingredient of interest, iterate through the passed ingredients_list
    for this_key in ingredients_dict.keys():
        this_key_ingredient = ingredients_dict[this_key]
        for this_ingredient in ingredients_list:
            ## Only consider ingredients if they contain the regex pattern
            if re.match(this_key_ingredient['pattern'], this_ingredient['ingredient']):
                ## Only consider standard unit amounts (either g or mL)
                if (this_ingredient['std_unit'] != None):
                    ## Convert std_unit to pref_unit if necessaryy
                    if (this_ingredient['std_unit'] != this_key_ingredient['pref_unit']):
                        this_key_ingredient['amounts'].append(this_ingredient['std_amount'] * this_key_ingredient['conversion_ratio'])
                    else:
                        this_key_ingredient['amounts'].append(this_ingredient['std_amount'])

        ## Get the total sum of amounts for this ingredient
        this_key_ingredient['sum_amount'] = sum(this_key_ingredient['amounts']) 

    ## Build return dict
    return_list = [{   
            'ingredient': key,
            'total': ingredients_dict[key]['sum_amount'] / (1000 if ingredients_dict[key]['pref_unit'] == 'g' else 10000),
            'unit': ('kG' if ingredients_dict[key]['pref_unit'] == 'g' else 'kL')
        } for key in ingredients_dict.keys()
    ]

    return return_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Serious Eats Dashboard Processing")
    parser.add_argument('--output-dir', '-o', type=str, default='./Data/SeriousEats/DashboardReady', help="Path to the output directory.")
    parser.add_argument('--recipe-processed-dir', type=str, default='./Data/SeriousEats/RecipesProcessed', help="Path to the directory containing processed recipe .json files.")
    parser.add_argument('--pre-processed-dir', type=str, default='./Data/SeriousEats/SiteContentPreProcessed', help="Path to the directory containing the extracted extracted schema .json files of Serious Eats webpages. This should also include a summary dictionary.")
    parser.add_argument('--raw-content-dir', type=str, default='./Data/SeriousEats/SiteContentRaw', help="Path to the directory containing the raw site files pulled from serious_eats_raw_data-ingest.py")

    ## Local file handling
    args = parser.parse_args()
    recipe_processed_content_loc = Path(f'{args.recipe_processed_dir}')
    pre_processed_content_loc = Path(f'{args.pre_processed_dir}')
    raw_content_loc = Path(f'{args.raw_content_dir}')

    dashboard_content_loc = Path(f'{args.output_dir}')
    dashboard_content_loc.mkdir(parents=True, exist_ok=True)

    last_run_epoch = os.path.getmtime(raw_content_loc)

    ## Load the pre-processing summary dict crated by serious_eats_data-_pre_processing.py
    with open(f'{pre_processed_content_loc}/00_preprocessing_summary.json', 'r') as summ_file:
        pre_processing_summary_dict = json.load(summ_file)
    summ_file.close()

    ## Temp lists to build dataframes of high-level recipe data suited for use in dashboard
    all_recipe_summ_dicts = []
    recipe_summ_keep_keys = ['name','datePublished', 'dateModified', 'recipeCategory', 'recipeCuisine', 'cookTime', 'totalTime', 'nutrition', 'author', 'description', 'aggregateRating', 'keywords', 'url']
    
    ## Temp lists to build dataframes of high-level ingredient data suited for use in dashboard
    all_ingredient_dicts = []
    ingredient_keep_keys = ['name', 'recipeIngredient']

    for this_file in os.listdir(recipe_processed_content_loc):
        if '00_' not in this_file: # Ignore summary files

            ## Read recipe data from serious_eats-Recipe_processing.py
            with open(f'{recipe_processed_content_loc}/{this_file}', 'r') as this_file:
                this_recipe_dict = json.load(this_file)
            this_file.close()

            ## Set None default for list of list fields
            if ('recipeCategory' not in this_recipe_dict.keys()) or (this_recipe_dict['recipeCategory'] == None):
                this_recipe_dict['recipeCategory'] = ['None']
            if 'recipeCuisine' not in this_recipe_dict.keys() or this_recipe_dict['recipeCuisine'] == None:
                this_recipe_dict['recipeCuisine'] = ['None']

            ## Ensure that url is included for each recipe
            if 'mainEntityOfPage' in this_recipe_dict.keys() and '@id' in this_recipe_dict['mainEntityOfPage'].keys():
                this_recipe_dict['url'] = this_recipe_dict['mainEntityOfPage']['@id']

            ## Build recipe summary dicts
            this_recipe_summ = {key: this_recipe_dict[key] for key in recipe_summ_keep_keys if key in this_recipe_dict}
            all_recipe_summ_dicts.append(this_recipe_summ)



            ## Build recipe ingredient dicts
            if 'recipeIngredient' in this_recipe_dict.keys():
                for this_ingredient in this_recipe_dict['recipeIngredient']:
                    this_ingredient_dict = {key: this_ingredient[key] for key in ingredient_keep_keys if key in this_ingredient}
                    all_ingredient_dicts.append(this_ingredient)



    ## Save basic page summary data to .json
    page_summ_dict = build_page_summary_dict(pre_processing_summary_dict, last_run_epoch)
    gf.save_dict_to_file(page_summ_dict, f'{dashboard_content_loc}/page_summary')

    ## Use pandas to save list of recipe dicts to .csv
    recipe_df = pd.json_normalize(all_recipe_summ_dicts, errors = 'ignore')
    recipe_df.to_csv(f'{dashboard_content_loc}/recipe_data.csv', index = False)

    ## Use pandas to save list of ingredient dicts to .csv
    ingredient_df = pd.json_normalize(all_ingredient_dicts, errors = 'ignore')
    ingredient_df.to_csv(f'{dashboard_content_loc}/ingredient_data.csv', index = False)

    ## Use pandas to save common ingredient summary data to .csv
    common_ingredient_df = pd.json_normalize(count_common_ingredients(all_ingredient_dicts))
    common_ingredient_df.to_csv(f'{dashboard_content_loc}/common_ingredients_summary.csv', index = False)