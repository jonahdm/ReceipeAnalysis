import curl_cffi

from datetime import datetime
import json
from pathlib import Path
import re
import xmltodict as xtd

## Below are constants for converting to standard metric units (gram for mass, mililiter for volume).
## CAVEAT: If "T" is used for tablespoon, it will be read and converted as teaspoon
## CAVEAT: Ounces are considered to be mass unless explicilty labeled as "fluid ounce" or "fl oz"
METRIC_PREFIX_CONVERSION = {None: 1, 'kilo': 1000, 'k': 1000, 'hecto': 100, 'h': 100, 'deca': 10, 'deka': 10, 'da': 10,
                            'deci': 0.1, 'd': 0.1, 'centi': 0.01, 'c': 0.01, 'mili': 0.001, 'm': 0.001}
GRAM_CONVERSIONS = {'gram': 1, 'g': 1, 'ounce': 28.3495, 'oz': 28.3495, 'pound': 453.592, 'lb': 453.592}
MILILITER_CONVERSIONS = {'liter': 1, 'litre': 1, 'l': 1,
                        'drop': 0.0513429 , 'dr': 0.0513429, 'smidgen': 0.115522, 'smdg': 0.115522, 'pinch': 0.231043, 'pn': 0.231043,
                        'dash': 0.462086 , 'ds': 0.462086, 'teaspoon': 4.92892 , 'tsp': 4.92892 , 't': 4.92892,
                        'tablespoon': 14.7868, 'tbsp': 14.7868, 'fluid ounce': 29.5735, 'fl oz': 29.5735,
                        'cup': 236.588 , 'c': 236.588, 'pint': 473.176, 'pt': 473.176, 'quart': 946.353, 'qt': 946.353,
                        'gallon': 3785.41, 'gal': 3785.41}

def standardize_unit(orig_amount: float, orig_unit: str, orig_prefix: str = None) -> tuple[float, str] :
    '''
    Converts a given amount of some unit into the equivalent in either grams or mililiters (depending on the original unit).
    This is far from comprehensive and is only intended for the narrow use of units seen in Serious Eats recipes.
    Note that in ambigous cases (oz), militers will be returned rather than grams.
    
    Args:
        orig_amount: The original value of the unit passed.
        orig_unit: The original unit prefix. See GRAM_CONVERSIONS and MILLILITER_CONVERSIONS constants for the full list of units this function can handle.
        orig_prefix: For metric units only, this handles prefixes ranging from mili to kilo.

    Returns:
        std_amount: The converted amount.
        std_unit: The units of conversion. Will be grams for mass and militers for volume.
    '''
    try:
        prefix_val = METRIC_PREFIX_CONVERSION[orig_prefix]
        unit_val = GRAM_CONVERSIONS[orig_unit] if orig_unit in GRAM_CONVERSIONS.keys() else MILILITER_CONVERSIONS[orig_unit]
 
        std_amount = orig_amount * (prefix_val * unit_val) * (1000 if orig_unit in ['liter', 'litre', 'l'] else 1) # For volume we want to keep units in mL
        std_unit = 'g' if orig_unit in GRAM_CONVERSIONS.keys() else 'mL'

    except:
        std_amount, std_unit = None, None

    return std_amount, std_unit

def make_web_request(url: str) -> curl_cffi.Response:

    '''
    Make a request and returns the result.

    Args:
        url: The web url to make a request from.

    Returns:
        Raw response from the url.
    '''
    url_response = curl_cffi.get(url, impersonate="chrome")
    return url_response

def save_dict_to_file(dictionary: dict|list, output_location: str) -> bool:
    '''
    Saves the output of a response at the specified file location and extension.

    Args:
        dictionary: The dictionary containing data to be saved.
        output_location: The path to desired directory for file output. File extension of .json is assumed.

    Returns:
        True if the process succeeded. Otherwise system will error.
    '''

    with open(f'{output_location}.json', "w") as file:
        json.dump(dictionary, file, indent = 4)
    file.close()

    return True

def save_response_content_to_file(request: curl_cffi.Response, output_location: str) -> bool:
    '''
    Saves the output of a response at the specified file location and extension.

    Args:
        sitemap_request: The requests.Response of a single url. Preferably generated from make_web_request().
        output_location: The path to desired directory for file output. This should include the file extension.

    Returns:
        True if the process succeeded. Otherwise system will error.
    '''

    with open(output_location, "wb") as file:
        file.write(request.content)
    file.close()
    return True

def get_user_agents_list() -> list[str]:
    '''
    Call this function to get a list of valid users agents from https://www.useragentlist.net/
    
    Returns:
        user_agents: A list of user agents suitable for presntation as headers in a web request.

    '''

    user_agents = []    
    url = 'https://www.useragentlist.net/'
    request = curl_cffi.get(url)
    
    user_agents = [t for t in request.text.split('\n') if 'Mozilla/5.0' in t] # Historic artifact makes for easy identification of acceptable agents
    user_agents = [re.search(r'<strong>(.*?)</strong>', t).group(1) for t in user_agents]
    
    return user_agents

def gen_user_agent_weights(user_agents_list: list[str]) -> list[int]:
    '''
    Generates a list of weights for a given list of user agents, with more favorable agents recieving higher weights.
    Criteria taken from https://scrapfly.io/blog/user-agent-header-in-web-scraping/

    Args:
        user_agents_list: A list of user agents. Preferably from get_user_agents_list()

    Returns:
        user_agents_weights : A list of integer weights that follow the same order of user agents as user_agent_list.

    '''

    user_agent_weights = [0 for agent in user_agents_list]
    
    for i in range(len(user_agents_list)):
        this_user_agent = user_agents_list[i]
        this_weight = 1000
        
        # Add higher weight based on the browser
        if 'Chrome' in this_user_agent:
            this_weight += 100
        if 'Firefox' or 'Edge' in this_user_agent:
            this_weight += 50
        if 'Chrome Mobile' or 'Firefox Mobile' in this_user_agent:
            this_weight += 0
            
        # Add higher weight based on the OS type
        if 'Windows' in this_user_agent:
            this_weight += 150
        if 'Mac OS X' in this_user_agent:
            this_weight += 100
        if 'Linux' or 'Ubuntu' in this_user_agent:
            this_weight -= 50
        if 'Android' in this_user_agent:
            this_weight -= 100
            
        user_agent_weights[i] += this_weight
    
    return user_agent_weights

def xml_file_to_dict(file_location: str) -> dict:
    '''
    Reads a .xml file and makes it a dictionary object
    
    Args:
        file_location: Path to the locally saved .xml file, preferably created by save_response_content_to_file()

    Returns:
        xml_dict: An xml tree represented as a dictionary. The keys of this dict represent the root of the xml tree.
    '''

    with open(Path(file_location), "r") as file:
        file_text = file.read()
    file.close()
    xml_dict = xtd.parse(file_text)
  
    return xml_dict

def read_file_as_str(file_location: str) -> str :
    '''
    Reads the text from a file.
    
    Args:
        file_location: Path to the locally saved (presumably .txt).

    Returns:
        file_string: The raw text of file.
    '''
    with open(Path(f'{file_location}'), 'rb') as this_file:
        file_string = this_file.read().decode('utf-8')
    this_file.close()

    return file_string

def get_many_urls(url_list: list[str], output_location: str, url_names_list: list[str] = False) -> dict:

    '''
    Makes requests on a list of urls, and saves the raw bytes (response.content) to a .txt file. Also creates a dictionary of calls and results for each url.    
    
    Args:
        url_list: Path to the locally saved .xml file, preferably created by save_response_content_to_file()
        output_location: Path to desired directory.
        url_names_list: A list of alternative file names that follows the same order of url_list. If not provided, files will be named as the "[raw__url].txt".

    Returns:
        results_dict: A dict with entries representing each attempted web request. Contains the url requested, whether the request was successful, and the epoch time of the attempt.
    '''
    results_dict = {
        i : {'url': url_list[i],
            'successful': False,
            'attempted_at' : None,
            'saved_as' : None,
            } 
        for i in range(len(url_list))
        }
    
    for i in range(len(url_list)):
        this_url = url_list[i]
        results_dict[i]['attempted_at'] = datetime.now().timestamp()
        try:
            file_name = f'{url_names_list[i] if url_names_list is not False else this_url}.txt'
            this_request = make_web_request(this_url)
            save_response_content_to_file(this_request, f'{output_location}/{file_name}')
            request_successful = True

        except Exception as E:
            print(f'Error Occured while requesting url: {this_url}.\n'
                    f'Error is: {E}')
            request_successful = False
        
        results_dict[i]['saved_as'] = file_name
        results_dict[i]['successful'] = request_successful

    return results_dict


if __name__ == '__main__':
    
    print('This file is not intended for individual execution, but to be imported for its functions by other modules. Exiting.')
    exit()
