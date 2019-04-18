from .template import Template
from .. import OntQuery
from ..cfg import config

from io import TextIOWrapper
from owlready2.namespace import Ontology
from rdflib import Graph
from yaml import load as yaml_load, SafeLoader
from yaml.parser import ParserError
import logging


class TemplateDriver():

    def __init__(self, template: Template, user_ont: Ontology,
                 user_graph: Graph, user_prefs: TextIOWrapper):
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
        
        # Building template data
        self.template_data = dict()

        # Ensuring order overrides and item overrides are valid
        order_overrides = self.__getOrderOverrides()
        item_overrides = self.__getItemOverrides()

        # Instantiating query agent
        self.query = OntQuery(ont=user_ont, graph=user_graph)

        # Dictionary to store user data
        self.user_data = dict()

        # Extracting template data from the ontology
        for ont_class in template.getRequiredClasses():
            # Isolating order override (if any)
            if ont_class in order_overrides.keys():
                order = order_overrides[ont_class]
            else:
                order = None

            # Getting all of type 'ont_class', with order restrictions
            class_invds = self.query.getAllOfType(c_type=ont_class, order=order)

            # Apply item overrides (if they exist for current `ont_class`)
            if ont_class in item_overrides.keys():
                # Keep if the individual ID is in item overrides
                # Note: This preserves ordering from retrieval function
                class_invds = [i for i in class_invds if i['$id']
                    in item_overrides[ont_class]]

            # Appending to user data dictionary
            self.user_data[ont_class] = class_invds
        
        print(self.user_data)

    def __getItemOverrides(self) -> dict:
        # Only proceed if item overrides are specified
        if 'item_overrides' not in self.user_prefs_attrs:
            return {}

        for item_type in self.user_prefs['item_overrides']:
            # Getting IDs of individuals of the given type
            try:
                indv_ids = set([i.name for i in
                    config.ont_classes[item_type].instances()])
            except KeyError:
                message = 'Item override type {0} in item overrides not valid'.\
                    format(item_type)
                logging.error(item_type)
                raise
            
            if not set(self.user_prefs['item_overrides'][item_type]).issubset(
                indv_ids):
                message = 'Item ID overrides {0} for type {1} are not valid'.\
                    format(set(self.user_prefs['item_overrides'][item_type])
                    .difference(indv_ids), item_type)
                logging.error(message)
                raise KeyError(message)

        return self.user_prefs['item_overrides']

    def __getOrderOverrides(self) -> dict:
        # Only proceed if order overrides are specified
        if 'order_overrides' not in self.user_prefs_attrs:
            return {}
        
        # Iterate through order overrides, and ensure they are valid
        for order_override in self.user_prefs['order_overrides']:
            override_type = self.user_prefs['order_overrides'][order_override]
            if override_type not in config.valid_order_options:
                message = 'Invalid order override option {0} for class {1}'.\
                    format(override_type, order_override)
                logging.error(message)
                raise ValueError(message)

        return self.user_prefs['order_overrides']
