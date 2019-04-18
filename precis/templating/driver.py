from .template import Template

from io import TextIOWrapper
from owlready2.namespace import Ontology
from yaml import load as yaml_load, SafeLoader
from yaml.parser import ParserError
import logging


class TemplateDriver():
    def __init__(self, template: Template, user_data: Ontology,
                 user_prefs: TextIOWrapper):
        # Parsing user preferences, saving to class variable
        try:
            self.user_prefs = yaml_load(stream=user_prefs, Loader=SafeLoader)
            self.user_prefs_attrs = set(self.user_prefs.keys())
        except ParserError:
            message = 'User preferences file {0} is malformed'.format(
                user_prefs.name)
            logging.error(message)
            raise

        # Checking all attributes required by the template are present in
        # user configuration file
        if not template.getRequiredInput().issubset(self.user_prefs_attrs):
            message = 'Required user preferences {0} are missing'.format(
                template.getRequiredInput().difference(self.user_prefs_attrs))
            logging.error(message)
            raise AttributeError(message)
        
        logging.debug('User prefs validated with all required keys present')
        
