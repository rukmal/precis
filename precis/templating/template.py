from . import util
from ..cfg import config

from jinja2 import Environment, TemplateSyntaxError
from yaml import load as yaml_load, SafeLoader
import logging
import os


class Template():
    def __init__(self, template_folder: str):
        # Validating candidate template
        util.validateTemplate(template_folder=template_folder)
        logging.debug('Successfully validated template in {0}'.format(
            template_folder))

        # Binding template file to class variable
        self.template_file = os.path.join(template_folder,
                                          config.template_files['template'])
        logging.debug('Isolated template Jinja file {0}'.format(
            self.template_file))
                                        
        # Loading template configuration, binding to class variable
        with open(os.path.join(template_folder,
            config.template_files['config'])) as f:
            self.template_config = yaml_load(stream=f, Loader=SafeLoader)
            logging.debug('Loaded template configuration file {0}'.format(
                f.name))

    def getTemplateConfiguration(self) -> dict:
        """Function to get the complete template configuration.
        
        Returns:
            dict -- Template configuration.
        """

        return self.template_config

    def getName(self) -> str:
        """Function to get the full name of the template.
        
        Returns:
            str -- Full name of the template.
        """

        return self.template_config['full_name']
    
    def getDescription(self) -> str:
        """Function to get the description of the template.
        
        Returns:
            str -- Template description.
        """

        return self.template_config['description']
    
    def getAuthor(self) -> str:
        """Function to get the author of the template.
        
        Returns:
            str -- Template author.
        """

        return self.template_config['author']

    def getIncludedClasses(self) -> list:
        """Function to get the included classes (from the Precis ontology) used
        in the template.
        
        Returns:
            list -- Classes (from Precis Ontology) included in the template.
        """

        return self.template_config['required_input']

    def render(self, render_data: dict):
        # render the template here
        pass
