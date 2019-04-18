from test_cfg import TestConfig
from context import precis

from owlready2 import get_ontology

import unittest


class TestTemplate(unittest.TestCase):
    
    def test_validateTemplate(self):
        precis.templating.Template(
            template_folder=TestConfig.template_cv
        )
        self.assertTrue(True)

    def test_validateAllTemplates(self):
        """Function to validate all templates in the `templates` folder.

        This function tests the functionality of the util module's
        `listAllTemplateFolders` and `validateTemplate` functions.
        """

        # Get all template folders
        template_folders = precis.templating.util.listAllTemplateFolders()

        # Iterate through each and validate
        for template_folder in template_folders:
            precis.templating.util.validateTemplate(
                template_folder=template_folder
            )

        # If no errors, we passed
        self.assertTrue(True)

    def test_templateDriver(self):
        """Function to test the TemplateDriver functionality of the templating
        engine. Validates that the 'cv' template can be rendered.
        """

        # Importing CV template
        cv_template = precis.templating.Template(
            template_folder=TestConfig.template_cv
        )

        # Loading user ontology
        user_ont = get_ontology(TestConfig.sample_rdf_data)

        # Loading user preferences (for the template)
        user_prefs = open(TestConfig.template_prefs, 'r')

        # Instantiating template driver
        driver = precis.templating.TemplateDriver(
            template=cv_template,
            user_data=user_ont,
            user_prefs=user_prefs
        )
