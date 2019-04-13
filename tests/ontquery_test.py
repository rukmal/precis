from test_cfg import TestConfig
from context import precis

from owlready2 import get_ontology, default_world

import unittest


class TestOntQuery(unittest.TestCase):
    """Test the `OntQuery` module.
    """

    def __init__(self, *args, **kwargs):
        # Running superclass initialization
        super(TestOntQuery, self).__init__(*args, **kwargs)

        # Loading ontology
        self.ont = get_ontology(TestConfig.sample_rdf_data).load()
        # Casting to graph
        self.graph = default_world.as_rdflib_graph()

        # Instantiating OntQuery for tests
        self.query = precis.OntQuery(ont=self.ont, graph=self.graph)

    def test_getIndividual(self):
        """Tests the 'getIndividual' functionality of OntQuery.
        """

        # Expecting the following keys (subset of all)
        expected_keys = set(['degreeConcentration', 'degreeType', 'hasDate',
                           'hasName', 'inCity'])
        
        # Attempting to load individual
        target_individual = self.ont.search_one(iri='*degree_bs_econ')

        # Getting candidate individual
        candidate = self.query.getIndividual(individual=target_individual)

        # Casting keys to set
        candidate_keys = set(candidate.keys())

        # Ensuring difference between sets is empty, meaning all expected
        # keys were present in the candidate key set
        self.assertEqual(len(expected_keys.difference(candidate_keys)), 0)

    def test_getAllOfType(self):
        """Tests the 'getAllOfType' functionality of OntQuery.
        """

        # Expecting the following IDs
        expected_ids = set(['we_spacex_ceo', 'we_tesla_ceo'])

        # Attempting to load all of 'WorkExperience' class
        candidate = self.query.getAllOfType(c_type='WorkExperience')

        # Extracting IDs
        candidate_ids = set([i['$id'] for i in candidate])

        # Ensuring difference between sets is empty, meaning all expected
        # IDs were present in the candidate ID set
        self.assertEqual(len(expected_ids.difference(candidate_ids)), 0)

    def test_getAll(self):
        """Tests the 'getAll' functionality of OntQuery.
        """

        # Expecting the following classes (even though they will be empty)
        expected_classes = set(['WorkExperience', 'Accolade', 'SkillGroup',
                                'Course', 'KnowledgeArea'])

        # Attempting to load entire ontology
        candidate = self.query.getAll()

        # Casting keys to set
        candidate_classes = set(candidate.keys())

        # Ensuring difference between sets is empty, meaning all expected
        # classes were present in the candidate classes set
        self.assertEqual(len(expected_classes.difference(candidate_classes)), 0)
