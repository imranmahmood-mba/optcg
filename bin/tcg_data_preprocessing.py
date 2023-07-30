import re 
import logging
import logging.config
import numpy as np
import os

# Get the absolute directory of the current script
abs_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the logging configuration file
logging_config_path = os.path.join(abs_dir, '..', 'util', 'logging_to_file.conf')

logging.config.fileConfig(fname=logging_config_path)

# Get the custom Logger from Configuration File
logger = logging.getLogger(__name__)

def convert_to_number(s):
    """
    Converts a currency string with $ prefix to a float.

    Parameters:
        s (str): The currency string to convert.

    Returns:
        float: The converted currency as a float, or None if conversion failed.
    """
    s = s.replace("$", "")
    try:
        value = float(s)
        logger.info(f'Successfully ran convert_to_number, resulting in {s} as the value')
    except ValueError:
        value = np.nan
    except Exception as e:
        logger.error(f'Error in the method convert_to_number(): {e}')
        raise e
    else:
        return value

def get_card_name(s):
    """
    Extracts the name of the card from a string by removing the text within parentheses and leading/trailing white spaces.

    The function assumes the card name is the text preceding the first '(' character in the string.
    It is intended to extract character name, effect name, etc., when these details are specified within parentheses in the full card name.

    Parameters:
        s (str): The string containing the full card name.

    Returns:
        str: The extracted card name, or the entire original string if no parentheses are present.
    """
    try:
        # Find the positions of the characters
        pos_parenthesis = s.find('(')
        pos_dash = s.find('- ')

        # If '(' appears before '-' or '-' is not found
        if pos_parenthesis != -1 and (pos_dash == -1 or pos_parenthesis < pos_dash):
            s = s.split('(')[0].strip()
        # If '-' appears before '(' or '(' is not found
        elif pos_dash != -1 and (pos_parenthesis == -1 or pos_dash < pos_parenthesis):
            s = s.split('- ')[0].strip()
        # If neither '-' nor '(' is found
        else:
            s = s.strip()
        logging.info(f"Successfully extracted card name: {s}")
    except Exception as e:
        logging.error(f"There was an issue with method get_card_name(): {e}")
        raise e
    else:
        return s

def get_card_type(s):
    """
    Extracts the type(s) of a card from a string by finding all the substrings within parentheses.
    
    This function scans the input string for any substrings that are surrounded by parentheses and 
    checks if they are present in a predefined list of card types. If a match is found, it is added 
    to a list of matched card types. This function returns all matched card types.

    Parameters:
        s (str): The string containing the full card name and type(s).

    Returns:
        list: A list of all matched card types. The list is empty if no card types were found.
    """
    try:
        matches = re.findall(r'\((.*?)\)', s)
        card_type_list = ['Alternate Art', 'Parallel', 'Box Topper', 'Promotion Pack', 
                        'Store Championship Participation Pack', 'Tournament Pack Vol.', 'Winner Pack Vol.', 'Manga']
        
        matched_items = []
        for match in matches:
            if any(item in match for item in card_type_list):
                matched_items.append(match)
        logging.info(f"Successfully extracted card type(s): {matched_items}")
    except Exception as e:
        logging.error(f"There was an issue with method get_card_type(): {e}")
    else:
        return matched_items