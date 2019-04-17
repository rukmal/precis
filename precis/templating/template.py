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

    def render(self, render_data: dict):
        # render the template here
        pass
