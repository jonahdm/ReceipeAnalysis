import argparse
import altair as alt
from datetime import datetime, timedelta
import isodate
import json
import pandas as pd
from pathlib import Path
import streamlit as st

from Dashboard import dashboard_home, dashboard_recipe_explorer, dashboard_menu_builder, dashboard_general_functions as dgf

st.set_page_config(layout="wide")

@st.cache_data()
def clean_common_ingredient_summary_data(this_df: pd.DataFrame) -> pd.DataFrame:
    this_df['ingredient'] = [this_ingredient.replace('_', ' ') for this_ingredient in this_df['ingredient']]
    this_df['total'] = this_df['total'].round(2)
    return this_df

## The app launches with "streamlit run dashboard_main.py" so namespace is not strictly necessary. It is included here to keep formatting convetion with other files.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Serious Eats Dashboard")
    parser.add_argument('--dashboard-ready-dir', type=str, default='Data/SeriousEats/DashboardReady', help="Path to the directory containing dashboard ready data. Presumably created by serious_eats_dashboard_data_prep.py .")

    ## Local file handling
    args = parser.parse_args()
    dashboard_content_loc = Path(f'{args.dashboard_ready_dir}')

    ## Load initial datasets into app. These are cached.
    page_summary_dict = dgf.load_file(f'{dashboard_content_loc}/page_summary.json')
    common_ingredient_df = clean_common_ingredient_summary_data(dgf.load_file(f'{dashboard_content_loc}/common_ingredients_summary.csv'))
    recipe_df = dgf.load_file(f'{dashboard_content_loc}/recipe_data.csv')
    ingredient_df = dgf.load_file(f'{dashboard_content_loc}/ingredient_data.csv')

    ## Build and populate navigation tabs for each page
    home, recipe_explorer, menu_builder = st.tabs(['Home', 'Explore Recipes', 'Build Menus'])
    with home:
        dashboard_home.build(page_summary_dict, common_ingredient_df, recipe_df)
    with recipe_explorer:
        dashboard_recipe_explorer.build(recipe_df)
    with menu_builder:
        dashboard_menu_builder.build(recipe_df)


