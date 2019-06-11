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

        logging.debug('Preparing query to extract instances of type {0} in\
            ascending temporal order'.format(c_type))

        return prepareQuery("""
            SELECT DISTINCT ?s
            WHERE {{
                {{
                    ?s rdf:type precis:{c_type} .
                }}
                OPTIONAL
                {{
                    ?s precis:hasDate ?date .
                }}
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

        logging.debug('Preparing query to extract instances of type {0} in\
            descending temporal order'.format(c_type))

        return prepareQuery("""
            SELECT DISTINCT ?s
            WHERE {{
                {{
                    ?s rdf:type precis:{c_type} .
                }}
                OPTIONAL
                {{
                    ?s precis:hasDate ?date .
                }}
            }}
            ORDER BY DESC(?date)
            """.format(c_type=c_type),
            initNs=self.initN)

    @classmethod
    def getAllOfTypeAlphabeticalAsc(self, c_type: str) -> Query:
        """Function to get all instances of a given type in ascending
        alphabetical order (based on `hasName` property).
        
        Arguments:
            c_type {str} -- Target type (eg: 'Degree', 'WorkExperience', etc.).
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug('Preparing query to extract instances of type {0} in\
            ascending alphabetical order'.format(c_type))
        
        return prepareQuery("""
            SELECT DISTINCT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
                ?s precis:hasName ?name .
            }}
            ORDER BY ASC(UCASE(STR(?name)))
            """.format(c_type=c_type),
            initNs=self.initN)

    @classmethod
    def getAllOfTypeAlphabeticalDesc(self, c_type: str) -> Query:
        """Function to get all instances of a given type in descending
        alphabetical order (based on `hasName` property).
        
        Arguments:
            c_type {str} -- Target type (eg: 'Degree', 'WorkExperience', etc.).
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug('Preparing query to extract instances of type {0} in\
            descending alphabetical order'.format(c_type))
        
        return prepareQuery("""
            SELECT DISTINCT ?s
            WHERE {{
                ?s rdf:type precis:{c_type} .
                ?s precis:hasName ?name .
            }}
            ORDER BY DESC(UCASE(STR(?name)))
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

        logging.debug('Preparing query to get object properties for {0}'.format(
            target_iri))

        return prepareQuery("""
                SELECT DISTINCT ?p ?name ?orgname ?parentOrgName
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
                            UNION
                            {{
                                {{
                                    ?o precis:hasParentOrganization ?org .
                                    ?org precis:hasName ?orgname .
                                }}
                                OPTIONAL
                                {{
                                    ?org precis:hasParentOrganization ?parentOrg .
                                    ?parentOrg precis:hasName ?parentOrgName .
                                }}
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

        logging.debug('Preparing description query for individual {0}'.format(
            target_iri))

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

    @classmethod
    def getAffiliated(self, target_iri: str) -> Query:
        """SPARQL query to get instances that have listed the current
        `target_iri` as an `affiliatedWith` instance.
        
        Arguments:
            target_iri {str} -- Target instance IRI.
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug('Preparing affiliated with query for individual {0}'.\
            format(target_iri))

        return prepareQuery("""
            SELECT DISTINCT ?related ?label
            WHERE {{
                ?related precis:affiliatedWith <{target_iri}> .
                ?related rdf:type ?type .
                ?type rdfs:label ?label .
            }}
            """.format(target_iri=target_iri),
            initNs=self.initN)

    @classmethod
    def getRelatedNameOfType(self, target_iri: str, c_type: str) -> Query:
        """SPARQL query to get the name of 'relatedTo` entities of a specific
        type, given a `target_iri`, and `c_type`.
        
        Arguments:
            target_iri {str} -- Target instance IRI.
            c_type {str} -- Target type (eg: 'Skill', 'WorkExperience', etc.)
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug('Preparing related name query for individual {0} with\
            type {1}'.format(target_iri, c_type))
        
        return prepareQuery("""
            SELECT ?name
            WHERE {{
                <{target_iri}> precis:relatedTo ?targets .
                ?targets rdf:type precis:{c_type} .
                ?targets precis:hasName ?name .
            }}
            """.format(target_iri=target_iri, c_type=c_type),
            initNs=self.initN)

    @classmethod
    def getAwards(self, target_iri: str) -> Query:
        """SPARQL query to get the name and affiliated organizations issuing
        awards from given a `target_iri` 'relatedTo' entities.
        
        Arguments:
            target_iri {str} -- Target instance IRI.
        
        Returns:
            Query -- Prepared query.
        """

        logging.debug('Preparing awards query for individual {0}'.\
            format(target_iri))

        return prepareQuery("""
            SELECT ?award_name ?org_name
            WHERE {{
                <{target_iri}> precis:relatedTo ?org .
                ?org precis:hasName ?org_name .
                ?award precis:affiliatedWith ?org .
                ?award rdf:type precis:Award .
                ?award precis:hasName ?award_name .
            }}
        """.format(target_iri=target_iri),
        initNs=self.initN)
