from ..cfg import config

from jinja2 import Environment, TemplateSyntaxError
import os
import logging
from yaml import load as yaml_load, SafeLoader


def listAllTemplateFolders() -> list:
    """Function to list all template folders in the project templates directory.
    
    This function intentionally does not validate the templates, but rather just
    returns candidate template folders for speed.
    
    Returns:
        list -- List of template folders.
    """

    # List to store output
    available_template_folders = []

    # Iterating through files in the templates folder
    for f in os.listdir(path=config.templates_folder):
        # Appending to templates folder to get full path
        f_path = os.path.join(config.templates_folder, f)
        # Check if directory, if so append to the list
        if os.path.isdir(f_path):
            available_template_folders += [f_path]

    return available_template_folders


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
            logging.debug('Template Jinja {0} validated'.format(template_file))
        except TemplateSyntaxError:
            message = 'Template file {0} is invalid'.format(template_file)
            logging.error(message)
            raise

    # Checking template configuration validity
    with open(template_config_file) as f:
        template_config_attrs = set(yaml_load(stream=f, Loader=SafeLoader)\
            .keys())
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
        else:
            logging.debug('Template configuration {0} validated'.format(
                template_config_file))

    logging.debug('Validated template in {0}'.format(template_folder))
