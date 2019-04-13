from context import precis


import unittest


class TestLoader(unittest.TestCase):
    
    def test_loaderSample(self):
        """Tests the loader with the sample resume file (Musk).
        """

        # Opening sample JSON file
        f = open('data/sample.json', 'r')

        # Testing Precis loader
        test = precis.Loader(ingest_file=f)

        self.assertTrue(True)
