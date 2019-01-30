import collections
import json
import logging


def buildData(data_file: str, override_files: list=[]) -> dict:
    """Initializes the static configuration variables used in the
    PaperRank system. Provides a method to override base configuration.

    Keyword Arguments:
        override {str} -- File name in the `config/` directory
            that may be used to override the `base.json` configuration
            (default: {''}).

    Raises:
        RuntimeError -- Raised when configuration files cannot be found.
    """

    # Parsing base data file
    data = parseJSON(file_path=data_file)

    # Iterate through override files, parse and apply each to base data file
    for override_file in override_files:
        override_data = parseJSON(file_path=override_file)
        data = applyOverride(base_dict=data, override_dict=override_data)

    return data


def parseJSON(file_path: str) -> dict:
    """Function to parse a JSON file.
    
    Arguments:
        file_path {str} -- File path of target JSON file.
    
    Raises:
        FileNotFoundError -- Raised if the target file is not found.
        JSONDecodeError -- Raised if there is an error parsing the JSON file.
    
    Returns:
        dict -- Dictionary of parsed JSON file contents.
    """

    try:
        data_str = open(file_path).read()
        data_parsed = json.loads(data_str)
        return data_parsed
    except FileNotFoundError as e:
        logging.error('File %s not found' % file_path)
        logging.error(e)
        raise e
    except json.decoder.JSONDecodeError as e:
        logging.error('Error parsing JSON file %s' % file_path)
        logging.error(e)
        raise e


def applyOverride(base_dict: dict, override_dict: dict) -> dict:
    """Function to apply an override to a dictionary with values from another.
    
    Arguments:
        base_dict {dict} -- Base dictionary.
        override_dict {dict} -- Override dictionary.
    
    Returns:
        dict -- Updated dictionary.
    """

    for k, v in override_dict.items():
        if isinstance(v, collections.Mapping):
            base_dict[k] = applyOverride(base_dict.get(k, {}), v)
        else:
            base_dict[k] = v
    return base_dict
