from .cfg import config

from collections import OrderedDict
from datetime import datetime
from io import TextIOWrapper
from owlready2 import default_world
from owlready2.entity import ThingClass
from owlready2.namespace import Ontology
from owlready2.rdflib_store import TripleLiteRDFlibGraph
from typing import Union
from urllib.parse import urlparse
from uuid import uuid4
import json
import logging
import re


class Loader():
    """This module encapsulates JSON loading functionality. It supports loading
    a nested JSON representation of the linked data resume, as described in the
    project README.

    Loader intelligently resolves cross-references in the JSON representation,
    and correctly handles nested classes. It also fails gracefully, and will
    complete with warnings unless a fatal error is encountered.

    The Loader functions by iteratively progressing through each of the objects
    in the top-level JSONArray, preserving the original order of the objects in
    the JSON file, and the keys within the objects themselves. This ensures that
    the user can reliably use nested-definitions of objects, and then use
    references to those objects later in the same file to establish relations
    between entities.

    The Loader also enforces object property and data property restrictions from
    the Precis ontology, enforcing the cardinality of these relations. The
    Loader will provide user-readable warnings, indicating the ID of the
    problematic object, and the relevant property that needs to be fixed.

    The Loader achieves this behavior by first iterating over object property
    relations, and - if a nested object is encountered - it will recursively
    instantiate the nested classes first, and then insert a reference to the
    newly created child object in the parent object. If a string is encountered
    as opposed to a nested object, it will search for the given ID in the
    ontology, and dynamically insert a reference to the object in the parent
    object, enabling easy ID-based cross-referencing.
    """

    def __init__(self, ingest_file: TextIOWrapper, namespace: str=None):
        """Initialization function for the Loader class. This method reads in a
        JSON file, and iteratively processes each of the objects in the
        top-level JSONArray.
        
        Arguments:
            ingest_file {TextIOWrapper} -- Target JSON file object.
        
        Keyword Arguments:
            namespace {str} -- Namespace to be used for the Ontology. A random
                               namespace is generated if one is not provided
                               (default: {None}).
        
        Raises:
            JSONDecodeError -- Raised when the input JSON file is malformed.
            FileNotFoundError -- Raised when the target JSON file is not found.
        """

        # Namespace creation (randomly generated if not explicitly provided)
        if namespace is None:
            config.namespace = config.ont.get_namespace(
                ''.join([config.ont_base_iri, str(uuid4())]))
        else:
            # Verifying custom namespace
            self.__verifyNamespace(candidate_namespace=namespace)
            config.namespace = config.ont.get_namespace(namespace)

        try:
            # Attempting to load JSON file
            # Note: the OrderedDict object hook is to preserve JSONArray order
            raw = json.load(ingest_file, object_pairs_hook=OrderedDict)
        except json.decoder.JSONDecodeError:
            logging.error('JSON file is malformed')
            raise
        except FileNotFoundError:
            logging.error('JSON file {0} not found'.format(ingest_file.name))
            raise

        for instance in raw:
            # Creating ontology class from each instance
            self.__processInstance(candidate_object=instance)
        
        logging.info('Success! Added {0} individuals to the Precis ontology\
            with base namespace IRI {1}'.format(
                len(list(config.ont.individuals())),
                config.namespace.base_iri)
            )

    def getOntology(self) -> Ontology:
        """Function to get the ontology as an owlready2 ontology.
        
        Returns:
            Ontology -- Built ontology with the loaded information.
        """

        return config.namespace.ontology
    
    def getRDFLibGraph(self) -> TripleLiteRDFlibGraph:
        """Function to get the rdflib graph representation of the ontology.
        
        Returns:
            TripleLiteRDFlibGraph -- RDFlib compatible graph.
        """

        return default_world.as_rdflib_graph()
    
    def saveToFile(self, save_location: str):
        """Function to save the built ontology to an RDF/XML file.
        
        Arguments:
            save_location {str} -- Location to save the file.
        """

        # Attempting to save to file, throw exception if not
        try:
            config.namespace.ontology.save(file=save_location, format='rdfxml')
        except:
            logging.error('Ontology could not be saved to {0}'.format(
                save_location))
            raise
    
    def getNamespace(self) -> str:
        """Function to retrieve the namespace of the created ontology. This is
        (obviously) most useful in the case that a custom namespace is not
        provided, and a randomly-generated namespace is used instead.
        
        Returns:
            str -- Namespace of the created ontology.
        """

        return config.namespace.base_iri

    def __processInstance(self, candidate_object: dict):
        """Function to instantiate and add a given class instance to the
        ontology. This iterates through - in order - the object property
        relations, the data property relations, and finally the description
        objects.
        
        This function intelligently handles nested objects, and manages
        ID-based references correctly.
        
        Arguments:
            candidate_object {dict} -- Candidate object to be added to
                                       the ontology.
        """

        # Empty container for the object to be added
        new_individual = dict()

        # Isolating type and id, removing from dictionary
        try:
            individual_id = candidate_object['$id']
            del candidate_object['$id']
            individual_type = candidate_object['$type']
            del candidate_object['$type']
        except KeyError:
            message = 'Missing required key "$type" or "$id$ in {0}'.format(
                candidate_object)
            logging.error(message)
            raise KeyError(message)

        # Isolating list of object properties (if any exist)
        # Note: Explicit loop is necessary here to preserve order
        obj_properties = []
        for candidate_property in candidate_object.keys():
            if candidate_property in config.object_properties.keys():
                obj_properties.append(candidate_property)

        # Isolating list of data properties (if any exist) [order is irrelevant]
        data_properties = list(set(candidate_object.keys()).intersection(set(
            config.data_properties.keys())))

        # Iterating through object property relations
        for obj_property in obj_properties:
            new_individual[obj_property] = self.__handleObjectProperty(
                object_property=obj_property,
                i_type=individual_type,
                i_id=individual_id,
                candidate_obj=candidate_object[obj_property])

            # Removing existing key from the candidate object dictionary
            del candidate_object[obj_property]
        
        # Iterating through data properties
        for data_property in data_properties:
            # Isolate candidate property
            candidate_property = candidate_object[data_property]

            # Handle data property correctly, assign to new dictionary
            new_individual[data_property] = self.__handleDataProperty(
                data_property=data_property,
                i_type=individual_type,
                i_id=individual_id,
                candidate_property=candidate_property
            )

            # Remove key from the candidate object dictionary
            del candidate_object[data_property]

        # If descriptions exist, process accordingly
        if 'hasDescription' in candidate_object.keys():
            new_individual['hasDescription'] = self.__handleDescription(
                obj_id=individual_id,
                obj_type=individual_type,
                descr_obj=candidate_object['hasDescription'])

            # Remove key from the candidate object dictionary
            del candidate_object['hasDescription']

        # Verify that all keys in the candidate object were removed, log
        if len(candidate_object.keys()) != 0:
            logging.warn('Keys {0} in the object with ID {1} are unrecognized\
                and were ommitted'.format(
                    str(candidate_object.keys()), individual_id
            ))

        # Logging
        logging.debug('Adding object with ID {0} of type {1}'.format(
            individual_id, individual_type))

        # Creating instance by calling class constructor
        config.ont_classes[individual_type](
            individual_id,
            namespace=config.namespace,
            **new_individual
        )

    def __handleObjectProperty(self, object_property: str, i_type: str,
        i_id: str, candidate_obj: object) -> Union[list, ThingClass]:
        """Function to handle an object property relation, given the type of
        the parent objct, and the candidate object JSON. This function
        intelligently introspects the candidate object, and will recursively
        add a nested JSON object to the ontology, or resolve an ID reference
        to an existing individual in the ontology.
        
        This function also enforces property cardinality restrictions,
        based on the specific parent object type.
        
        Arguments:
            object_property {str} -- Object property.
            i_type {str} -- Type of the parent object.
            i_id {str} -- ID of the parent objectt.
            candidate_obj {object} -- Candidate object to be added as property.
        
        Raises:
            TypeError -- Raised if the cardinality of the property is incorrect.
        
        Returns:
            Union[list, ThingClass] -- Returns either a ThingClass object of
                                       the child type, or a list of ThingClass
                                       objects, depending on the restrictions.
        """

        # Cast to list for simplicty, include flag for later
        isList: bool = type(candidate_obj) is list
        if not isList: candidate_obj = [candidate_obj]

        ret_obj = []

        for obj in candidate_obj:
            if type(obj) is OrderedDict:
                # Nested object, process first
                obj_id = obj['$id']
                self.__processInstance(candidate_object=obj)
                # Find newly added object, add to return object
                obj = obj_id

            # Lookup and add to return object
            ret_obj += [self.__findInOntology(search_id=obj, obj_id=i_id)]

        # Check if functional property w.r.t. current class, if so return as-is
        # if not cast to list and return (incl. lookup stuff obviously)
        # See: http://bit.ly/2YY8rzz (search for 'FunctionalProperty')
        if config.object_properties[object_property].is_functional_for(config.
            ont_classes[i_type]):
            if isList:
                message = 'Property {0} in the object {1} should not be a list'\
                    .format(object_property, i_id)
                logging.error(message)
                raise TypeError(message)
            return ret_obj[0]
        else:
            return ret_obj

    def __handleDataProperty(self, data_property: str, i_type: str, i_id: str,
        candidate_property: object) -> Union[int, str, float, list]:
        """Function to handle a data property relation, given the type of the
        parent object, and the candidate property JSON. This function
        intelligently introspects the candidate object, and will resolve ensure
        that the type of the candidate property matches the property
        restriction outlined in the ontology.

        This function also enforces data property cardinality restrictions,
        based on the specific parent object type.
        
        Arguments:
            data_property {str} -- Data property.
            i_type {str} -- Type of the parent object.
            i_id {str} -- ID of the parent object.
            candidate_property {object} -- Candidate property to be added.
        
        Raises:
            TypeError -- Raised if the cardinality of the property is incorrect.
        
        Returns:
            Union[int, str, float, list] -- Returns one of the listed types,
                                            depending on the restrictions. 
        """

        # Special handler for date-like data properties
        date_like_properties = ['hasDate', 'endDate']
        if data_property in date_like_properties:
            candidate_property = self.__processDateLike(
                date_like_property=candidate_property,
                property_name=data_property,
                i_id=i_id
            )

        # Check if functional property w.r.t. current class, if so add as-is
        # if not cast to list and append (if not list)
        # See: http://bit.ly/2YY8rzz (search for 'FunctionalProperty')
        if config.data_properties[data_property].is_functional_for(config.
            ont_classes[i_type]):
            if type(candidate_property) is list:
                message = 'Property {0} in the object {1} should not be a list'\
                    .format(data_property, i_id)
                logging.error(message)
                raise TypeError(message)
            return candidate_property
        elif type(candidate_property) is not list:
            return [candidate_property]
        else:
            # Already a list, return as-is
            return candidate_property

    def __handleDescription(self, obj_id: str, obj_type: str,
        descr_obj: object) -> Union[ThingClass, list]:
        """Function to handle Description objects. This function will
        intelligently ensure that the cardinality of the provided descriptions
        matches the property restriction of the parent object type.
        
        Arguments:
            obj_id {str} -- ID of the parent object.
            obj_type {str} -- Type of the parent object.
            descr_obj {object} -- Description object to be added.
        
        Raises:
            TypeError -- Raised if the cardinality of the property is incorrect.
        
        Returns:
            Union[ThingClass, list] -- Returns either a single Description
                                       ThingClass object, or a list of
                                       ThingClass objects, based on the
                                       cardinality restrictions.
        """

        # Cast to list for simplicity, include flag for later
        isList: bool = type(descr_obj) is list
        if not isList: descr_obj = [descr_obj]
        
        ret_obj = []

        for idx, descr in enumerate(descr_obj):
            if 'hasPriority' in descr.keys():
                priority = descr['hasPriority']
            else:
                priority = 0
            ret_obj.append(config.ont.Description(
                f"{obj_id}-description-{idx}",
                namespace=config.namespace,
                hasPriority=priority,
                hasText=descr['hasText']
            ))
        
        # Check if functional property w.r.t. current class, if so add as-is
        # if not cast to list and append (if not list)
        # See: http://bit.ly/2YY8rzz (search for 'FunctionalProperty')
        if config.ont.hasDescription.is_functional_for(config
            .ont_classes[obj_type]):
            if isList:
                message = 'Description in the object {0} should not be a list'\
                    .format(obj_id)
                logging.error(message)
                raise TypeError(message)
            return ret_obj[0]
        else:
            return ret_obj

    def __findInOntology(self, search_id: str, obj_id: str) -> ThingClass:
        """Function to find a specific individual in the current ontology,
        given a search ID. This function appends the correct base IRI to the
        search ID, and locates the individual in the current ontology, given
        that the search ID is valid.
        
        Arguments:
            search_id {str} -- ID to be searched for in the Ontology.
            obj_id {str} -- ID of the parent (i.e. driving) object.
        
        Raises:
            ReferenceError -- Raised if the search ID does not yield a result.
        
        Returns:
            ThingClass -- ThingClass individual corresponding to search_id.
        """

        # Building complete candidate IRI
        candidate_iri = config.namespace.base_iri + search_id

        # Locating instance in the ontology
        res = config.ont.search(iri=candidate_iri)

        # Ensure existence
        if len(res) == 0:
            message = 'Entity {0} referenced before assignment in {1}'.format(
                search_id, obj_id)
            logging.error(message)
            raise ReferenceError(message)
        
        return res[0]

    def __processDateLike(self, date_like_property: str, property_name: str,
                          i_id: str) -> datetime:
        """Function to process a date-like property (i.e. a date string), and
        to return it as a datetime object to satisfy the object type
        restriction.
        
        Arguments:
            date_like_property {str} -- Date like string to be processed.
            property_name {str} -- Name of the data property.
            i_id {str} -- Parent object ID.
        
        Raises:
            TypeError -- Raised if the type of the date string is incorrect.
            ValueError -- Raised if the format of the date string is incorrect.
        
        Returns:
            datetime -- Python datetime object corresponding to the date string.
        """

        # Checking type
        if type(date_like_property) is not str:
            message = 'Property {0} in the object {1} must be a date string'\
                .format(property_name, i_id)
            logging.error(message)
            raise TypeError(message)
        
        # Extracting date from date string, raise error if malformatted
        # Note: See https://regexr.com/ for Regex explanation
        date_regex = '([0-9]{4})-([0-9]{2})-([0-9]{2})'
        date_match = re.match(pattern=date_regex, string=date_like_property)

        # Raise error if not correct type
        if not date_match:
            message = 'Property {0} in object {1} in malformatted. Must be\
                in the format YYYY-MM-DD'.format(property_name, i_id)
            logging.error(message)
            raise ValueError(message)
        
        # Build datetime object and return
        return datetime(year=int(date_match[1]),
                        month=int(date_match[2]),
                        day=int(date_match[3]))

    def __verifyNamespace(self, candidate_namespace: str):
        """Verification function to check that a given custom namespace is
        a valid URI.
        
        Arguments:
            candidate_namespace {str} -- Candidate namespace URI to be checked.
        
        Raises:
            ValueError -- Raised when the candidate namespace is not valid.
        """

        # Validating URL components with urlparse
        # See: http://bit.ly/2GkTdgI
        parsed_url = urlparse(url=candidate_namespace)

        # If any of these are missing, it is not a valid namespace URI
        if not all([parsed_url.scheme, parsed_url.netloc]):
            message = 'Provided namespace {0} is invalid'.format(
                candidate_namespace)
            logging.error(message)
            raise ValueError(message)
