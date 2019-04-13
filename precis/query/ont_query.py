from .sparql_queries import SPARQLQueries

from collections import OrderedDict
from owlready2.namespace import Ontology
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
import logging


class OntQuery():
    def __init__(self, ont: Ontology, graph: Graph, namespace: str):
        # Assigning class variables
        self.ont = ont
        self.graph = graph

        # Setting namespaces for the top-level ontology, and instance graph
        self.precis_namespace = Namespace(self.ont.base_iri)
        self.inst_namespace = Namespace(namespace)

    def findOfType(self, c_type: str, temporal_order: str=None) -> OrderedDict:
        # To do:
        # - Add flag for temporal ordering (asc/descending)
        # - Change order date variable dyanically if it is 'WorkExperience'
        # - Add check for date in the object type, before searching for it

        # Checking temporal order validity
        if (temporal_order) and (temporal_order not in ['A', 'D']):
            message = 'Temporal order must be one of either "A" or "D"'
            logging.error(message)
            raise ValueError(message)

        # Dynamically assign query based on type
        if (temporal_order == 'A'):
            query = SPARQLQueries.getAllOfTypeAscendingTemporal(c_type=c_type)
        elif (temporal_order == 'D'):
            query = SPARQLQueries.getAllOfTypeDescendingTemporal(c_type=c_type)
        else:
            query = SPARQLQueries.getAllOfType(c_type=c_type)

        # Execute query
        results = self.graph.query(query_object=query)
        
        for row in results:
            print(row)
