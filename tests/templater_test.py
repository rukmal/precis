from test_cfg import TestConfig
from context import precis

import unittest


class TestTemplater(unittest.TestCase):
    def test_templaterDriver(self):
        driver = precis.TemplateDriver(target_ont='data/sample.rdf',
                                       namespace=TestConfig.namespace)
