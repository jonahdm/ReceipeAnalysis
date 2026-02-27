'''
This file is meant to serve as a "one click" execution of the entire data pipeline, essentially replicating a pipelien configuration file.
'''

import subprocess
import sys

if __name__ == '__main__':

    ## Step 1: Get page data from SeriousEats.com
    subprocess.run([sys.executable, 'DataPipeline/serious_eats_raw_data_ingest.py', '--output-dir', 'Data/SeriousEats/SiteContentRaw',
                    '--full-refresh', 'False'])

    ## Step 2: Pre-Process page data
    subprocess.run([sys.executable, 'DataPipeline/serious_eats_data_pre_processing.py', '--output-dir', 'Data/SeriousEats/SiteContentPreProcessed',
                    '--raw-content-dir', 'Data/SeriousEats/SiteContentRaw'])

    ## Step 3: Process category specific page data. These steps could be safely executed in parallel
    subprocess.run([sys.executable, 'DataPipeline/serious_eats_recipe_processing.py', '--output-dir', 'Data/SeriousEats/RecipesProcessed',
                    '--pre-processed-dir', 'Data/SeriousEats/SiteContentPreProcessed'])

    ## Step 4: Prep processed data for use in Dashboard
    subprocess.run([sys.executable, 'DataPipeline/serious_eats_dashboard_data_prep.py', '--output-dir', 'Data/SeriousEats/RecipesProcessed',
                    '--recipe-processed-dir', 'Data/SeriousEats/RecipesProcessed',
                    '--pre-processed-dir', 'Data/SeriousEats/SiteContentPreProcessed',
                    '--raw-content-dir', 'Data/SeriousEats/SiteContentRaw'
                    ])
