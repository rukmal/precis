from io import TextIOWrapper
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from owlready2 import get_ontology
import logging


class TemplateDriver():
    def __init__(self, target_ont: TextIOWrapper, namespace: str):
        try:
            # Attempting to load RDF file with rdflib
            self.ont = get_ontology(target_ont).load()
        except:
            logging.error('Ontology at %s could not be loaded.' %\
                (target_ont.name))
            raise
