from ..cfg import config
from .sparql_queries import SPARQLQueries

from owlready2 import IRIS
from owlready2.entity import ThingClass
from owlready2.namespace import Ontology
from rdflib import Graph
import logging


class OntQuery():
    """This module encapsulates traversal functionality over the ontology.

    It enables data extraction from the Ontology by class type (i.e. 'Degree',
    'Course', 'WorkExperience', etc.), and provides additional functionality to
    order results by time. This is particularly useful for obtaining a list of
    chronologically-ordered 'WorkExperience's, for example.

    OntQuery uses a combination of SQPARQL queries (encapsulated in the
    SPARQLQueries module), and owlready2-enabled graph traversal to enable this
    behavior. This class intelligently populates and returns name labels from
    nested objects, referred to with the 'relatedTo' and 'affiliatedWith'
    object properties to name a few.

    OntQuery enables information extraction from the ontology filtering by
    class, instance IRI, or the entire ontology.
    """

    def __init__(self, ont: Ontology, graph: Graph):
        """OntQuery initialization method. Binds the target ontology, and
        RDFLib graph to class variables.
        
        Arguments:
            ont {Ontology} -- Ontology to be traversed.
            graph {Graph} -- RDFLib graph representation of the target ontology.
        """

        # Assigning class variables
        self.ont = ont
        self.graph = graph

    def findAllOfType(self, c_type: str, temporal_order: str=None) -> list:
        """Function to find all instances of a given class type, providing the
        option for temporally ordering the results in either ascending or
        descending order (using the `hasDate` data property).
        
        Arguments:
            c_type {str} -- Target class type (i.e. 'Degree', 'Course', etc.).
        
        Keyword Arguments:
            temporal_order {str} -- Temporal ordering, optional. Must be either
                                    'A' for ascending (i.e. old to new), or 'D'
                                    for descending (default: {None}).
        
        Raises:
            ValueError -- Raised when the `temporal_order` is not 'A' or 'D'.
        
        Returns:
            list -- Ordered (optional) list of all instances of `c_type`, with
                    intelligently expanded nested metadata. 
        """

        # Empty list to store output (naturally preserves order of course)
        output = list()

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

        for result in results:
            # Isolating candidate IRI and instance
            candidate_iri: str = result[0].toPython()
            candidate_individual: ThingClass = IRIS[candidate_iri]
            logging.debug('Processing search result instance {0}'
                .format(candidate_iri))
            # Getting python-ified instance data
            output.append(self.getIndividual(individual=candidate_individual))

        return output

    def getIndividual(self, individual: ThingClass) -> dict:
        """Function to get metadata for a given individual.
        
        This function intelligently nests metadata from related objects
        (eg: with object properties 'affiliatedWith', and 'relatedTo') in a
        list of lists, with secondary organization labels nested in each list.
        
        This will enable effective dynamic templating and display options.
            
        Arguments:
            individual {ThingClass} -- Target individual.
        
        Returns:
            dict -- Dictionary of metadata for the target individual.
        """

        # Output dictionary
        output = dict()

        # Appending ID of the object to the output dictionary, as this may be
        # used later for filtering
        output['$id'] = individual.name

        # Isolating individual IRI
        individual_iri: str = individual.get_iri()

        # Extracting all data properties for the given individual
        dataprop_query = SPARQLQueries.getDataProperties(
            target_iri=individual_iri
        )
        for result in self.graph.query(query_object=dataprop_query):
            # Getting datatype name
            datatype_iri = result[0].toPython()
            datatype_name = self.ont.search_one(iri=datatype_iri).python_name
            # Getting Python object of value
            value = result[1].toPython()
            # Adding to output dictionary (append to array if multiple)
            output.setdefault(datatype_name, []).append(value)

        # Extracting all object properties for the given individual
        objectprop_query = SPARQLQueries.getObjectProperties(
            target_iri=individual_iri
        )
        for result in self.graph.query(query_object=objectprop_query):
            # Getting object property name
            objectprop_iri = result[0].toPython()
            objectprop_name = self.ont.search_one(
                iri=objectprop_iri).python_name
            # Getting Python object of value, and appending orgname (optionally)
            value = [result[1].toPython()]
            # If it has orgname, append to result
            if result[2]:
                value.append(result[2].toPython())
            # Adding to output dictionary (append to array if multiple)
            output.setdefault(objectprop_name, []).append(value)

        # Extracting all description text for the given individual
        descr_query = SPARQLQueries.getOrderedDescriptionText(
            target_iri=individual_iri
        )
        for descr_object in self.graph.query(query_object=descr_query):
            descr_text = descr_object[0].toPython()
            # Appending to description list (ordered)
            output.setdefault('hasDescription', []).append(descr_text)

        logging.debug('Extracted {0} data fields for individual {1}'.format(
            len(output.keys()), individual_iri
        ))

        return output
