import ast
import html
import json
import pandas as pd
import streamlit as st

def reduce_list_to_substrings(inp_list: list) -> list:
    return_list = [
        this_item for this_item in inp_list if not any(other_item in this_item and this_item != other_item for other_item in inp_list)
    ]
    return return_list

@st.cache_data()
def get_unique_list_of_lists(inp_list: list, reduce_to_substrings: bool = True) -> list:
    inp_list_corrected = [item if type(item) is str else "['None']" for item in inp_list]
    return_list = [item for subitem in inp_list_corrected for item in ast.literal_eval(subitem)]
    return_list = list(set(return_list))
    return_list.sort()
 
    if reduce_to_substrings:
        return_list = reduce_list_to_substrings(return_list)
    return return_list

@st.cache_data()
def get_unique_list_from_list(inp_list: list, reduce_to_substrings: bool = False) -> list:
    return_list = list(set(inp_list))
    return_list.sort()
    if reduce_to_substrings:
        return_list = reduce_list_to_substrings(return_list)
    return return_list

@st.cache_data()
def load_file(file_location: str) -> dict | pd.DataFrame:
    if file_location.endswith('.json'):
        with open(f'{file_location}', 'r') as this_file:
            this_dict = json.load(this_file)
        this_file.close()
        return this_dict
    elif file_location.endswith('.csv'):
        this_df = pd.read_csv(f'{file_location}')
        this_df = this_df.map(lambda col: html.unescape(col) if isinstance(col, str) else col) # Decode text columns in the dataframe to display html
        return this_df
    
if __name__ == '__main__':
    print('This file is not intended for individual execution, but to be imported for its functions by other modules. Exiting.')
    exit()
