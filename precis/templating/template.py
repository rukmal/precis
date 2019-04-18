from . import util
from ..cfg import config

from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
from yaml import load as yaml_load, SafeLoader
import logging
import os


class PrecisTemplate():
    """This module encapsulates template functionality.

    Given a template folder, it verifies the validity of the template, by
    evaluating that the Jinja is valid, and that the template configuration
    has the required attributes (outlined in main precis configuration, cfg.py).

    Furthermore, this class also provides getters to access the complete
    configuration for a template, and provides functionality to render the
    underlying template, given user data.
    """

    def __init__(self, template_folder: str):
        """Template initialization method. Validates a candidate template, given
        its folder path. Binds necessary data to class variables to enable
        getter functionality.
        
        Arguments:
            template_folder {str} -- Path to the template folder.
        """

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

        # Setting up Jinja2 environment and template
        # See: http://bit.ly/2VTzOcb
        self.env = Environment(loader=FileSystemLoader(
                searchpath=template_folder
            ), **config.jinja_env_config)
        self.template = self.env.get_template(
                name=config.template_files['template']
            )

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

    def getRequiredInput(self) -> set:
        """Function to get the required user input needed by the template.
        
        Returns:
            set -- Required fields to be provided in the user preferences.
        """

        return set(self.template_config['required_input'])

    def getRequiredClasses(self) -> set:
        """Function to get the required ontology classes required by
        the template.
        
        Returns:
            set -- Classes required by the template.
        """
        
        return set(self.template_config['required_classes'])

    def renderTemplate(self, render_data: dict) -> str:
        """Function to render the template file, given rendering data pusuant
        to the restrictions in the template configuration file.
        
        Arguments:
            render_data {dict} -- Data for the template.
        
        Returns:
            str -- Rendered template.
        """

        return self.template.render(render_data)
