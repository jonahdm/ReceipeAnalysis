import altair as alt
from datetime import datetime, timedelta
import isodate
import pandas as pd
import streamlit as st

def build_common_ingredient_chart(common_ingredient_df: pd.DataFrame):
    common_ingredient_chart = alt.Chart(
        common_ingredient_df,
        title = alt.Title('What would you need to make one of everything?',
                          anchor = 'middle'
                          )
        ).mark_bar().encode(
        x = alt.X('ingredient', title = None, sort = '-y', axis=alt.Axis(labelAngle=-45)),
        y = alt.Y('total', title = 'kG', axis=alt.Axis(titleAngle=360)), 
    )
    return common_ingredient_chart

def build(page_summary_dict: dict, common_ingredient_df: pd.DataFrame, recipe_df: pd.DataFrame):
    
    ## Write top line intro
    st.header(f'There are {page_summary_dict['Recipes']:,} Recipes written by {page_summary_dict['Profiles']:,} Authors on Serious Eats (As of {datetime.fromtimestamp(page_summary_dict['AsOf']):%m/%d/%Y})',
               text_alignment = 'center')
    
    ## Setup columns for split display
    col1, col2, = st.columns([.6, .4], border = True)

    ## Populate Column 1 with common ingredient data
    col1.altair_chart(build_common_ingredient_chart(common_ingredient_df))
    
    ## Populate Column 2 with misc data
    col2.subheader(f'One serving of every recipe would produce more than {round(recipe_df['nutrition.calories.amount'].sum()):,} Calories')
    col2.text(f'(Enough to feed {(round(recipe_df['nutrition.calories.amount'].sum()/2000)):,} adults for one day)')

    sum_recipe_seconds = sum(recipe_df['totalTime.minValue'].fillna(recipe_df['totalTime']).apply(lambda x: isodate.parse_duration(x).total_seconds()))
    col2.subheader(f'And take over {timedelta(seconds = sum_recipe_seconds).days:,} days to make!')

    ## Write bottom line header
    st.header(f'Want to see more that Serious Eats has to offer? Explore more with the tabs at the top of the page!',
               text_alignment = 'center')

