import ast
import pandas as pd
import streamlit as st

from Dashboard import dashboard_general_functions as dgf

## TODO: Build this as a class in dashboard_general_functions
COURSE_DEFINITIONS = [
    {'displayName': "Appetizer",
     'categories': ['Appetizer', 'Biscuit', 'Bread', 'Cornbread', 'Guacamole', 'Hummus', 'Jam', 'Jelly', 'Popcorn', 'Rolls', 
                    'Salsa', 'Side', 'Snack']
     },
    {'displayName': "Soup",
    'categories': ['Gaspacho', 'Soup'],
     },
    {'displayName': "Salad",
    'categories': ['Salad']
     },
    {'displayName': "Entrée",
    'categories': ['Breakfast', 'Brunch', 'Burger', 'Crepe', 'Chili', 'Dinner', 'Entree', 'French Toast', 'Hot Dog', 'Lunch', 
                   'Mains', 'Pancake', 'Pasta', 'Pizza', 'Sandwich', 'Sausage', 'Stew', 'Waffle']
     },
    {'displayName': "Dessert",
    'categories': ['Bars', 'Blondies', 'Brownies', 'Cake', 'Candy', 'Caramel', 'Cheesecakes', 'Cookies', 'Crumbles', 'Cupcakes', 'Custard', 'Dessert',
                   'Doughnuts', 'Gelato', 'Ice Cream', 'Milkshake', 'Muffins', 'Pastry', 'Pie', 'Popsicles', 'Puddings', 'Sorbet', 'Sherbet', 'Tarts']
     },
    {'displayName': "Drink",
    'categories': ['Beer','Beverage','Brandy', 'Cocoa', 'Cocktail', 'Coffee', 'Cognac', 'Drinks', 'Gin', 'Lemonade', 'Liqueur', 'Mezcal',
                   'Non-Alcoholic', 'Rum', 'Sangria', 'Smoothie', 'Tea', 'Tequila', 'Vodka', 'Wine', 'Whiskey']
     }
]

def format_course_display(course_index: int) -> str:
    return COURSE_DEFINITIONS[course_index]['displayName']


def build(recipe_df):
    
    ## Intro header
    st.header('Need help planning the perfect menu?')
    
    ## Get unique lists from the recipe data. These are used to populate widget selections
    unique_cuisines = dgf.get_unique_list_of_lists(recipe_df['recipeCuisine'].str.strip())

    ## Set up initial selection options for users
    mainCol1, mainCol2 = st.columns(2)
    course_select = mainCol1.pills('Courses to Include', options = [course for course in range(len(COURSE_DEFINITIONS))], format_func = format_course_display, selection_mode = 'multi')
    preferred_cuisine = mainCol2.multiselect('Preferred Cuisines', unique_cuisines)
    st.divider()

    ## Make a list of data dicts associated with each user selected course
    course_dicts = [{'displayName': format_course_display(course)} for course in range(len(course_select))]
    selectCol1, selectCol2 = st.columns([.1, .9])
    for this_course in range(len(course_dicts)):
        course_display_name = COURSE_DEFINITIONS[course_select[this_course]]['displayName']

        ## Allow user input to update course filters
        course_dicts[this_course]['count'] = selectCol1.number_input(f'Number of {course_display_name}s', min_value = 1, max_value = 3, step = 1)
        course_dicts[this_course]['cuisine'] = selectCol2.multiselect(f'{course_display_name} styles', unique_cuisines, default = preferred_cuisine)
        
        ## Copy the base recipe dataframe and filter it to user specifications
        course_dicts[this_course]['dataFrame'] = recipe_df[['name', 'recipeCategory', 'recipeCuisine', 'url']].copy()
        course_dicts[this_course]['dataFrame'] = course_dicts[this_course]['dataFrame'][(course_dicts[this_course]['dataFrame']['recipeCategory'].apply(lambda this_row: any(this_category in this_row for this_category in COURSE_DEFINITIONS[course_select[this_course]]['categories'])))]
        course_dicts[this_course]['dataFrame'] = course_dicts[this_course]['dataFrame'][(course_dicts[this_course]['dataFrame']['recipeCuisine'].apply(lambda this_row: any(this_cuisine in this_row for this_cuisine in course_dicts[this_course]['cuisine'])) if course_dicts[this_course]['cuisine'] else [True for i in course_dicts[this_course]['dataFrame'].index])]

    ## Iterate through course dicts and display randomly sampled recipes based on user speicifcations
    if course_dicts != []:
        st.header('Your Menu')
        st.divider()

        for this_course in range(len(course_dicts)):
            ## Copy the already filtered course-specific dataframe
            this_dataframe = course_dicts[this_course]['dataFrame'][['name', 'url']]

            ## Ensure there are enough recipes that meet criteria before sampling and displaying
            if (course_dicts[this_course]['count'] + 1) <= this_dataframe.index.size:
                this_dataframe = this_dataframe.sample(course_dicts[this_course]['count'], replace = False)
                for i in range(0, course_dicts[this_course]['count']):
                    this_recipe = this_dataframe.iloc[i]
                    st.markdown(f'''
                    ## {COURSE_DEFINITIONS[course_select[this_course]]['displayName']}{f" {i + 1}" if course_dicts[this_course]['count'] > 1 else ""}
                    ### [{this_recipe['name']}]({this_recipe['url']})
                    ''')
                    st.divider()
            else:
                for i in range(0, this_dataframe.index.size):
                    this_recipe = this_dataframe.iloc[i]
                    st.markdown(f'''
                    ## {COURSE_DEFINITIONS[course_select[this_course]]['displayName']}{f" {i + 1}" if this_dataframe.index.size > 1 else ""}
                    ### [{this_recipe['name']}]({this_recipe['url']})
                    ''')
                    st.divider()
            