from test_cfg import TestConfig
from context import precis

import unittest


class TestTemplate(unittest.TestCase):
    
    def test_validateTemplate(self):
        # precis.templating.util.validateTemplate(
        #     template_folder=TestConfig.template_cv
        # )
        pass

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
