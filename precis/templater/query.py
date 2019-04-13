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

    def findOfType(self, c_type: str) -> OrderedDict:
        query = prepareQuery("""
            SELECT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
            }}
        """.format(c_type=c_type), initNs={'precis': self.precis_namespace})
        
        res = self.graph.query(query)

        for row in res:
            print(row)
