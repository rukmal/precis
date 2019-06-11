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
    order results by time, and alphabetically. This is particularly useful for
    obtaining a list of chronologically-ordered 'WorkExperience's, for example.

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

    def getAllOfType(self, c_type: str, order: str=None) -> list:
        """Function to find all instances of a given class type, providing the
        option for temporally ordering the results in either ascending or
        descending order (using the `hasDate` data property).
        
        Arguments:
            c_type {str} -- Target class type (i.e. 'Degree', 'Course', etc.).
        
        Keyword Arguments:
            order {str} -- Ordering, optional. Must be either 'chron_A',
                           'chron_D', 'alphabetical_A', or 'alphabetical_D', for
                           ascending and descending chronological order, and
                           ascending and descending alphabetical order,
                           respecitvely (default: {None}).
        
        Raises:
            ValueError -- Raised when the `order` is not 'chron_A', 'chron_D',
                          'alphabetical_A', or 'alphabetical_D'.
        
        Returns:
            list -- Ordered (optional) list of all instances of `c_type`, with
                    intelligently expanded nested metadata. 
        """

        # Empty list to store output (naturally preserves order of course)
        output = list()

        # Ensuring order selection is valid (if one is provided)
        if (order) and (order not in config.valid_order_options):
            message = 'Order must be one of {0}'.format(
                config.valid_order_options)
            logging.error(message)
            raise ValueError(message)

        # Dynamically assign query based on type
        if (order == 'chron_A'):
            query = SPARQLQueries.getAllOfTypeAscendingTemporal(c_type=c_type)
        elif (order == 'chron_D'):
            query = SPARQLQueries.getAllOfTypeDescendingTemporal(c_type=c_type)
        elif (order == 'alphabetical_A'):
            query = SPARQLQueries.getAllOfTypeAlphabeticalAsc(c_type=c_type)
        elif (order == 'alphabetical_D'):
            query = SPARQLQueries.getAllOfTypeAlphabeticalDesc(c_type=c_type)
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
            # Building list of nested object property chain
            objectprop_chain = [i.toPython() for i in result[1:]
                if i is not None]
            # Append object property chain to global output object list
            output.setdefault(objectprop_name, []).append(objectprop_chain)

        # Extracting all individuals that indicated they were 'affiliatedWith'
        # the current individual
        affiliated_query = SPARQLQueries.getAffiliated(
            target_iri=individual_iri
        )
        for result in self.graph.query(query_object=affiliated_query):
            # Creating dictionary to store formatted result
            affiliated_res = dict()
            # Isolating result IRI
            affiliated_iri = result[0].toPython()
            # Isolating result type
            affiliated_res['type'] = result[1].toPython()
            # Isolating result name
            affiliated_res['hasName'] = self.ont.search_one(iri=affiliated_iri)\
                .hasName
            # Appending to global output object
            output.setdefault('affiliated', []).append(affiliated_res)

        # Extracting all description text for the given individual
        descr_query = SPARQLQueries.getOrderedDescriptionText(
            target_iri=individual_iri
        )
        for descr_object in self.graph.query(query_object=descr_query):
            descr_text = descr_object[0].toPython()
            # Appending to description list (ordered)
            output.setdefault('hasDescription', []).append(descr_text)

        logging.debug('Queried {0} data fields for individual {1}'.format(
            len(output.keys()), individual_iri
        ))

        return output

    def getAll(self, order: str=None) -> dict:
        """Function to get the entire ontology, in a nested dictionary.

        Keyword Arguments:
            order {str} -- Ordering, optional. Must be either 'chron_A',
                           'chron_D', 'alphabetical_A', or 'alphabetical_D', for
                           ascending and descending chronological order, and
                           ascending and descending alphabetical order,
                           respecitvely (default: {None}).
        
        Raises:
            ValueError -- Raised when the `order` is not 'chron_A', 'chron_D',
                          'alphabetical_A', or 'alphabetical_D'.
        
        Returns:
            dict -- Ordered (optional) nested dictionary of all individuals in
                    the given ontology.
        """

        output = dict()

        # Iterate through list of ontology classes (from config)
        for c_type in config.ont_classes.keys():
            # Skip Description objects (blank nodes)
            if c_type == 'Description': continue
            
            # Get all individuals of the given type, bind to output
            output[c_type] = self.getAllOfType(
                c_type=c_type,
                order=order
            )

        return output


class TemplateOntQuery():
    """This module encapsulates generic template ontology query overrides
    to be applied when the data object is being built for the template.

    The dictionary `override_functions` serves as the registry for these
    override functions. Currently, class-based overides can be applied. This
    module provides functionality to both check if an override function exists
    for a given class, and to run the override, given a class and a set of JSON
    represented class individuals (in the format output by `precis.OntQuery`).
    """

    def __init__(self, ont: Ontology, graph: Graph):
        """TemplateOntQuery initialization method. Binds the target ontology, and
        RDFLib graph to class variables.
        
        Arguments:
            ont {Ontology} -- Ontology to be traversed.
            graph {Graph} -- RDFLib graph representation of the target ontology.
        """

        # Override function map
        # (also acts as registry of these functions)
        self.override_functions = {
            'Project': self.overrideProject
        }

        # Assigning instance variables
        self.graph = graph
        self.ont = ont

    def overrideExists(self, c_type: str) -> bool:
        """Flag to check if an override function exists for a given
        ontology class.
        
        Arguments:
            c_type {str} -- Target class type.
        
        Returns:
            bool -- True if override function exists, false otherwise.
        """

        return c_type in self.override_functions.keys()

    def overrideByClass(self, c_type: list, class_invds: list) -> list:
        """Function to run the registry override function over a list of JSON
        represented class individuals, given the list of individuals and the
        class name.
        
        Arguments:
            c_type {list} -- Target class type (eg: `Degree` or `Skill`).
            class_invds {list} -- List of JSON-represented individuals for the
                                  given class (in the format output by
                                  `precis.OntQuery`).
        
        Raises:
            KeyError: Raised when a class is provided for which an override
                      function does not exist.
        
        Returns:
            list -- List of JSON-represented (dict) individuals,
                    with override applied.
        """

        if c_type not in self.override_functions.keys():
            message = 'Invalid class type {0} for template override query'.\
                format(c_type)
            logging.error(message)
            raise KeyError(message)

        return self.override_functions[c_type](
            c_type=c_type,
            class_invds=class_invds
        )

    def overrideProject(self, c_type: list, class_invds: list) -> list:
        """Override function for the Project class.

        Adds a list of alphabetically sorted Skill Names, corresponding to each
        entity's relatedTo list, with the key 'relatedSkills'.
        Adds a list of awards, corresponding to each entity's relatedTo list,
        with the key 'awards'.
        
        Arguments:
            c_type {list} -- Target class type (eg: `Degree` or `Skill`).
            class_invds {list} -- List of JSON-represented individuals for the
                                  given class (in the format output by
                                  `precis.OntQuery`).
        
        Returns:
            list -- List of JSON-represented (dict) individuals,
                    with override applied.
        """

        # Iterating through each project; getting names of 'relatedTo' skills
        for proj in class_invds:
            # Isolating IRI of the current individual (not stored in JSON)
            target_iri = self.ont.search_one(iri=''.join(
                ['*', proj['$id']])).iri

            # Building query for the object
            proj_query = SPARQLQueries.getRelatedNameOfType(
                target_iri=target_iri,
                c_type='Skill'
            )

            # Running related named skill entity query
            name_objects = self.graph.query(query_object=proj_query)

            # Extracting related skill names and sorting alphabetically
            proj['relatedSkills'] = sorted([result[0].toPython()
                for result in name_objects])

            # Building awards query
            awards_query = SPARQLQueries.getAwards(target_iri=target_iri)

            # Running awards query
            awards_objects = self.graph.query(query_object=awards_query)

            # Building dictionary of key-value pairs from org -> award
            proj['awards'] = [
            {
                'award_name': i[0].toPython(),
                'org_name': i[1].toPython()
            }
            for i in awards_objects]
            print(proj['awards'])

        # Returning full list (modified)
        return class_invds
