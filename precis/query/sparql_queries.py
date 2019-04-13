from ..cfg import config

from rdflib import Namespace, OWL
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
        'precis': config.ont_base_iri,
        'owl': OWL
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
            SELECT DISTINCT ?s
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
            SELECT DISTINCT ?s
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
            SELECT DISTINCT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
                ?s precis:hasDate ?date .
            }}
            ORDER BY DESC(?date)
            """.format(c_type=c_type),
            initNs=self.initN)

    @classmethod
    def getDataProperties(self, target_iri: str) -> Query:
        """SPARQL query to return the data properties of a given instance,
        given its IRI.
        
        Arguments:
            target_iri {str} -- Target instance IRI.
        
        Returns:
            Query -- Prepared query.
        """

        return prepareQuery("""
                SELECT DISTINCT ?p ?o
                WHERE {{
                    <{target_iri}> ?p ?o .
                    ?p rdf:type owl:DatatypeProperty .
                }}
            """.format(target_iri=target_iri),
            initNs=self.initN)

    @classmethod
    def getObjectProperties(self, target_iri: str) -> Query:
        """SPARQL query to return the object properties of a given instance,
        given its IRI.

        This query also resolves second-level labels; that is, if a given object
        property is referring to a 'WorkExperience' instance, it will also
        return the name of the organization that is related to that
        'WorkExperience'. Similarly, it will also return the 'degreeUniversity'
        of a 'Degree' instance.

        This second-level label resolution is done intelligently, and it will
        never return more than a single second level label, as a second-level
        reference cannot be both a 'Degree' and 'WorkExperience' because they
        are independent classes.
        
        Arguments:
            target_iri {str} -- Target instance IRI.
        
        Returns:
            Query -- Prepared query.
        """

        return prepareQuery("""
                SELECT DISTINCT ?p ?name ?orgname
                WHERE {{
                    <{target_iri}> ?p ?o .
                    ?p rdf:type owl:ObjectProperty .
                    {{
                        {{
                            ?o precis:hasName ?name .
                        }}
                        OPTIONAL
                        {{
                            {{
                                ?o precis:employedAt ?org .
                                ?org precis:hasName ?orgname .
                            }}
                            UNION
                            {{
                                ?o precis:degreeUniversity ?org .
                                ?org precis:hasName ?orgname .
                            }}
                        }}
                    }}
                }}
            """.format(target_iri=target_iri),
            initNs=self.initN)

    @classmethod
    def getOrderedDescriptionText(self, target_iri: str) -> Query:
        """SPARQL query to get description text for a given instance IRI, as
        ordered by the 'hasPriority' attribute (in ascending order, so priority
        0 > 1 > 2 > ...).
        
        Arguments:
            target_iri {str} -- Target instance IRI.
        
        Returns:
            Query -- Prepared query.
        """

        return prepareQuery("""
                SELECT DISTINCT ?text
                WHERE {{
                    <{target_iri}> precis:hasDescription ?descr .
                    ?descr precis:hasPriority ?priority .
                    ?descr precis:hasText ?text .
                }}
                ORDER BY ?priority
            """.format(target_iri=target_iri),
            initNs=self.initN)
