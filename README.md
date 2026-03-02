# RecipeAnalysis
This is an in-progress project that scrapes and cleans recipe data available from online sources. It also includes an interactive analysis dashboard for exploration of recipe and author data. A demo dashboard is hosted on [Streamlit](https://jonahdm-recipes.streamlit.app/).

## Current Features

### [data_pipeline_main](data_pipeline_main.py)
A one-click execution script of all data pipeline files contained within the [DataPipeline](DataPipeline) directory. Scripts executed by this pipeline include:

* [raw_data_ingest](DataPipeline/serious_eats_raw_data_ingest.py): Pulls raw web data as pure text for over 16,000 pages of mixed types.
* [data_pre_processing](DataPipeline/serious_eats_data_pre_processing.py): Categorizes raw page data and extracts data schemas of interest.
* [recipe_processing](DataPipeline/serious_eats_recipe_processing.py): Cleans recipe schemas and standardizes data for specific fields (ingredients, nutrition, authorship, etc). 
* [dashboard_data_prep](DataPipeline/serious_eats_dashboard_data_prep.py): Performs summarizing functions and final cleaning for use in the data dashboard (see below). Data outputs would be considered "Gold" in a medallion data architecture.

### [dashboard_main](dashboard_main.py)
A user interface for exploring the recipe data, developed and executed through Streamlit. This script requires the contents of [Dashboard Ready Data Directory](Data/SeriousEats/DashboardReady/) to function. Each page in the dashboard is kept as a separate file within the [Dashboard](Dashboard) directory. Pages include:

* [home](Dashboard/dashboard_home.py): A basic landing page, containing several "KPIs" describing the data within.
* [recipe_explorer](Dashboard/dashboard_recipe_explorer.py): A simple exploration table that allows users to easily filter and find recipes which meet their specifications.
* [menu_builder](Dashboard/dashboard_menu_builder.py): A tool for building menus of up to 15 courses (plus drinks!) by selecting recipes according to user specifications.

## Usage
This is a project intended to demonstrate a basic ETL pipeline and dashboarding capability. The intention of all dashboarding is to better direct users to recipes that interest them **at the original host site of the recipe**. This tool is there to direct attention to recipe creators, without whom this type of project wouldn't be possible.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
The brilliant chefs at Serious Eats who have created the recipes used in this project. Their work is nothing but brilliant, and I don't start any meal without first consulting their site.

