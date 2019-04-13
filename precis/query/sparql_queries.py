from ..cfg import config

from rdflib import Namespace
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.sparql import Query
import logging

class SPARQLQueries():
    """This class contains getters for SPARQL queries used to extract
    information from the Precis ontology. Note that method of this class
    only returns pre-formed queries, and does not actually execute them.
    """

    # Class variable to store namespace
    initN = {
        'precis': config.ont_base_iri
    }

    @classmethod
    def getAllOfType(self, c_type: str) -> Query:
        """Function to get all instances of a given type from the ontology.
        
        Arguments:
            c_type {str} -- Target type (eg: 'Degree', 'WorkExperience', etc.).
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug("""Preparing query to extract instances of type {0}"""
            .format(c_type))

        return prepareQuery("""
            SELECT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
            }}
            """.format(c_type=c_type),
            initNs=self.initN)

    @classmethod
    def getAllOfTypeAscendingTemporal(self, c_type: str) -> Query:
        """Function to get all instances of a given type in ascending temporal
        order (based on `hasDate` property).
        
        Arguments:
            c_type {str} -- Target type (eg: 'Degree', 'WorkExperience', etc.).
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug("""Preparing query to extract instances of type {0} in\
            ascending temporal order""".format(c_type))

        return prepareQuery("""
            SELECT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
                ?s precis:hasDate ?date .
            }}
            ORDER BY ?date
            """.format(c_type=c_type),
            initNs=self.initN)
    
    @classmethod
    def getAllOfTypeDescendingTemporal(self, c_type: str) -> Query:
        """Function to get all instances of a given type in descending temporal
        order (based on `hasDate` property).
        
        Arguments:
            c_type {str} -- Target type (eg: 'Degree', 'WorkExperience', etc.).
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug("""Preparing query to extract instances of type {0} in\
            descending temporal order""".format(c_type))

        return prepareQuery("""
            SELECT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
                ?s precis:hasDate ?date .
            }}
            ORDER BY DESC(?date)
            """.format(c_type=c_type),
            initNs=self.initN)
