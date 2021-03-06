from test_cfg import TestConfig
from context import precis

import os

import unittest


class TestLoader(unittest.TestCase):
    
    def test_loaderSample(self):
        """Tests the loader with the sample resume file (Musk).
        """

        # Opening sample JSON file
        f = open(TestConfig.sample_json_data, 'r')

        # Testing Precis loader
        loader = precis.Loader(ingest_file=f)

        del loader

        # No errors, assume loading went well (lol @ this test, I know)
        self.assertTrue(True)

    def test_ontologyExport(self):
        """Verifies that the ontology can be loaded, returned and saved
        to a file. Deletes the file after verifying it exists, and is not empty.
        """

        # Opening sample JSON file
        f = open(TestConfig.sample_json_data, 'r')

        # Instantiating loader
        loader = precis.Loader(ingest_file=f)

        # Saving completed ontology to file
        loader.saveToFile(save_location=TestConfig.test_save_location)

        # Making sure file is not empty
        fileSize = os.stat(TestConfig.test_save_location).st_size

        # Deleting file
        os.remove(TestConfig.test_save_location)

        # Check file size
        self.assertTrue(fileSize > 0, 'RDF export did not work correctly.')

    def test_urlValidatorFail(self):
        """Tests that the provided namespace URI is validated correctly.
        """

        # Testing that the uri validator fails a poorly formatted uri
        fail_uri = 'this_is_not_a_valid_uri'

        # Opening sample JSON file
        f = open(TestConfig.sample_json_data, 'r')

        # Making sure the error is raised
        with self.assertRaises(ValueError):
            precis.Loader(ingest_file=f, namespace=fail_uri)

    def test_getNamespace(self):
        """Tests that the getter for the namespace works correctly.
        """

        # Test namespace
        test_namespace = 'http://precis.rukmal.me/ontology/this-is-a-test/'

        # Opening sample JSON file
        f = open(TestConfig.sample_json_data, 'r')

        # Creating loader object
        loader = precis.Loader(ingest_file=f, namespace=test_namespace)

        # Making sure the returned namespace matches
        self.assertEqual(test_namespace, loader.getNamespace())
