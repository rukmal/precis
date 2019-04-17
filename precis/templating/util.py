from ..cfg import config

from jinja2 import Environment, TemplateSyntaxError
import os
import logging
import yaml


def listAllTemplates() -> list:
    # List all folders
    # Validate each one
    # Give names of valid templates (maybe dict?)
    pass


def validateTemplate(template_folder: str):
    """Function to validate a template, given its folder path. Verifies that the
    folder contains the necessary files that compose a template, that the Jinja
    file is valid, and that the template configuration file has the
    necessary attributes.
    
    Arguments:
        template_folder {str} -- Path to the template folder.
    
    Raises:
        AttributeError -- Raised when the template configuration file does not
                          have the required attributes.
        FileNotFoundError -- Raised when the necessary files composing a
                             template are not found.
        TemplateSyntaxError -- Raised when the Jinja template is invalid.
    """

    template_file_set = set(os.listdir(path=template_folder))

    # Verifying template has required files
    if not set(config.template_files.values()).issubset(template_file_set):
        message = """Template is invalid; files {0} are required for a valid
            template.""".format(
                list(config.template_files.values()))
        logging.error(message)
        raise FileNotFoundError(message)

    # Building filenames
    template_config_file = os.path.join(template_folder,
                                        config.template_files['config'])
    template_file = os.path.join(template_folder,
                                 config.template_files['template'])

    # Checking template validity
    with open(template_file) as f:
        try:
            env = Environment()
            env.parse(source=f.read())
            logging.debug('Template {0} validated'.format(template_file))
        except TemplateSyntaxError:
            message = 'Template file {0} is invalid'.format(template_file)
            logging.error(message)
            raise

    # Checking template configuration validity
    with open(template_config_file) as f:
        template_config_attrs = set(yaml.load(stream=f).keys())
        if not set(config.template_config_required).issubset(
            template_config_attrs):
            message = """Template configuration files {0} is invalid.
            Missing attributes {1}""".format(
                    template_config_file,
                    set(config.template_config_required).
                        difference(template_config_attrs)
                )
            logging.error(message)
            raise AttributeError(message)

    logging.debug('Validated template in {0}'.format(template_folder))
