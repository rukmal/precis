from .. import OntQuery

from collections import OrderedDict
from rdflib.plugins.sparql import prepareQuery
from owlready2 import get_ontology, default_world
import logging


class TemplateDriver():
    def __init__(self, target_ont: str, namespace: str):
        try:
            # Attempting to load RDF file with rdflib
            self.ont = get_ontology(target_ont).load()
            # Casting to graph for SPARQL queries
            self.graph = default_world.as_rdflib_graph()
        except:
            logging.error('Ontology at %s could not be loaded.' %\
                (target_ont.name))
            raise

        # TEMPORARY - Will be loaded from template and user config, respectively
        self.targets = ['WorkExperience', 'Degree', 'Project', 'Publication']
        self.restrictions = {
            'WorkExperience': ['we_spacex_ceo', 'we_tesla_ceo']
        }

        # Instantiating OntQuery for query operations
        self.query = OntQuery(ont=self.ont, graph=self.graph,
                              namespace=namespace)

        for target in self.targets:
            target_restrictions = self.__getRestrictions(c_type=target)
            self.__getInstancesOfType(c_type=target,
                                      restrictions=target_restrictions)

    def __getInstancesOfType(self, c_type: str, restrictions: list)\
            -> OrderedDict:
        
        self.query.findOfType(c_type=c_type)
    
    def __getRestrictions(self, c_type: str) -> list:
        """Function to get the restrictions for a given class type. Returns an
        empty list if no restrictions are found.
        
        Arguments:
            c_type {str} -- Class type.
        
        Returns:
            list -- List of restrictions (if any).
        """

        try:
            return self.restrictions[c_type]
        except KeyError:
            return []
