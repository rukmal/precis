from . import util
from ..cfg import config

from jinja2 import Environment, TemplateSyntaxError
import logging
import os
import yaml


class Template():
    def __init__(self, template_folder: str):
        # Need to load template here
        self.template_folder = template_folder        
