import ast
import pandas as pd
import streamlit as st

from Dashboard import dashboard_general_functions as dgf

def build(recipe_df: pd.DataFrame):

    ## Get unique lists from the recipe data. These are used to populate widget selections
    unqiue_recipes = dgf.get_unique_list_from_list(recipe_df['name'].str.strip())
    unique_categories = dgf.get_unique_list_of_lists(recipe_df['recipeCategory'].str.strip())
    unique_cuisines = dgf.get_unique_list_of_lists(recipe_df['recipeCuisine'].str.strip())
    unique_authors = dgf.get_unique_list_from_list([this_author['name'].strip() for authors in recipe_df['author'] for this_author in ast.literal_eval(authors)])
   
    ## Set up filters for table
    st.header('Filter Recipes by Selection or Search')
    col1, col2, col3, col4, col5 = st.columns(5)

    ## Create widgets for user selection
    name_select = col1.multiselect('By Recipe', unqiue_recipes)
    category_select = col2.multiselect('By Category', unique_categories)
    cuisine_select = col3.multiselect('By Cuisines', unique_cuisines)
    author_select = col4.multiselect('By Author', unique_authors)
    rating_select = col5.select_slider('By Min. Aggregate Rating', options = [x / 2 for x in range(0, 11)], value =  0)

    ## Build filterable recipe dataframe
    filtered_recipe_df = recipe_df.copy()
    filtered_recipe_df = filtered_recipe_df[['name', 'url', 'recipeCategory', 'recipeCuisine', 'author']]

    ## Set get authorName and authorURL from author dict values in original df, then drop column of dicts from table
    filtered_recipe_df['authorName'] = [ast.literal_eval(authors)[0]['name'].strip() for authors in recipe_df['author']]
    filtered_recipe_df['authorURL']  = [ast.literal_eval(authors)[0]['url'] if 'url' in ast.literal_eval(authors)[0].keys() else None for authors in recipe_df['author']]
    filtered_recipe_df = filtered_recipe_df.drop('author', axis = 1)
    
    ## Append final columns
    filtered_recipe_df['aggregateRating.ratingValue'] = recipe_df['aggregateRating.ratingValue']

    ## Filter dataframe to requested categories based on user selections
    if name_select:
         filtered_recipe_df = filtered_recipe_df[(filtered_recipe_df['name'].apply(lambda this_row: any(this_name in this_row for this_name in name_select)) if name_select else [True for i in filtered_recipe_df.index])]
    if category_select:
         filtered_recipe_df = filtered_recipe_df[(filtered_recipe_df['recipeCategory'].apply(lambda this_row: any(this_category in this_row for this_category in category_select)) if category_select else [True for i in filtered_recipe_df.index])]
    if cuisine_select:
        filtered_recipe_df = filtered_recipe_df[(filtered_recipe_df['recipeCuisine'].apply(lambda this_row: any(this_cuisine in this_row for this_cuisine in cuisine_select)) if cuisine_select else [True for i in filtered_recipe_df.index])]
    if author_select:
        filtered_recipe_df = filtered_recipe_df[(filtered_recipe_df['authorName'].apply(lambda this_row: any(this_author in this_row for this_author in author_select)) if author_select else [True for i in filtered_recipe_df.index])]
    if rating_select > 0.0:
        filtered_recipe_df = filtered_recipe_df[(filtered_recipe_df['aggregateRating.ratingValue'].fillna(0.0) >= rating_select if rating_select != 0.0 else [True for i in filtered_recipe_df.index])]
    
    ## Display filtered dataframe with custom column formats
    st.dataframe(
        filtered_recipe_df,
        column_config = {
            'name': st.column_config.Column('Recipe'),
            'url': st.column_config.LinkColumn('Recipe Page', display_text = 'SeriousEats.com'),
            'recipeCategory': st.column_config.Column('Categories'),
            'recipeCuisine': st.column_config.Column('Cuisines'),
            'authorName': st.column_config.Column('Author'),
            'authorURL': st.column_config.LinkColumn('Author Page', display_text = 'SeriousEats.com'),
            'aggregateRating.ratingValue': st.column_config.Column('User Aggregate Rating')
            },
        hide_index = True
    )
 