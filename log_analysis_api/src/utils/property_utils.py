import os
from typing import Any
import yaml
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class DictToObject:
    """
    Contains methods to dictionary-object operations
    """
    
    def __init__(self, dictionary):
        """
        Accepts a dictionary and converts it into a python Object with relevant attributes

        Args:
            dictionary (_type_): a dictionary that needs to be converted into a Python Object
            with attributes.
        """
        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Recursively convert nested dictionaries to objects
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)
    
    def to_dict(self)-> dict:
        """
        Converts the object passed to a dictionary and returns the same.

        Returns:
            _type_: an instance of the dictionary object
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DictToObject):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
class PropertyLoader:
    """
    Contains methods to load properties file located in config folder 
    """

    def load_properties_from_yaml(file_path: str)->Any:
        """
        Takes the path to the properties file and returns none if no properties exist or a properties object
        these properties can be used for several configurable functions like filenames, headers, etc
        and are obtained from the yaml properties file path passed.

        Args:
            file_path (str): path to the yaml config file

        Returns:
            Any: formatted Properties dictionary object or None
        """
        file_path = os.path.join(BASE_DIR, file_path)
        with open(file_path, 'r') as file:
            try:
                properties = yaml.safe_load(file)
                return properties
            except yaml.YAMLError as e:
                print(f"Error loading YAML file: {e}")
                return None