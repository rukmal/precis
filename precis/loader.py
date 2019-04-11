from .cfg import config

from collections import OrderedDict
from owlready2.entity import ThingClass
from typing import Union
from uuid import uuid4
import json
import logging


class Loader():
    """This class encapsulated JSON loading functionality. It supports loading
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
    
    Raises:
        JSONDecodeError -- Raised when the input JSON file is malformed.
        FileNotFoundError -- Raised when the input JSON file is not found.
        TypeError -- Raised when the JSON object is of the incorrect type.
        ReferenceError -- Raised when an entity is referenced before assignment.
    """

    def __init__(self, ingest_file: str, namespace: str=None):
        """Initialization function for the Loader class. This method reads in a
        JSON file, and iteratively processes each of the objects in the
        top-level JSONArray.
        
        Arguments:
            ingest_file {str} -- File path of the target JSON file.
        
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
                'http://rukmal.me/precis/%s' % (str(uuid4())))
        else:
            config.namespace = config.ont.get_namespace(namespace)

        try:
            # Attempting to open candidate file
            f = open(file=ingest_file)
            # Loading JSON file
            # Note: the OrderedDict object hook is to preserve JSONArray order
            raw = json.load(f, object_pairs_hook=OrderedDict)
        except json.decoder.JSONDecodeError as e:
            logging.error('JSON file is malformed')
            raise e
        except FileNotFoundError as e:
            logging.error('JSON file %s not found')
            raise e

        for instance in raw:
            # Creating ontology class from each instance
            self.__processInstance(candidate_object=instance)
        
        logging.info('Success! Added %i individuals to the Precis ontology with\
            base namespace IRI %s' % (len(list(config.ont.individuals())),
            config.namespace.base_iri))

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
        individual_id = candidate_object['$id']
        del candidate_object['$id']
        individual_type = candidate_object['$type']
        del candidate_object['$type']

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
            self.__handleDescription(
                obj_id=individual_id,
                obj_type=individual_type,
                descr_obj=candidate_object['hasDescription'])

            # Remove key from the candidate object dictionary
            del candidate_object['hasDescription']

        # Verify that all keys in the candidate object were removed, log
        if len(candidate_object.keys()) != 0:
            logging.warn('Keys %s in the object with ID %s are unrecognized and\
                were ommitted' % (str(candidate_object.keys()), individual_id))

        # Logging
        logging.info('Adding object with ID %s of type %s' %\
            (individual_id, individual_type))

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
                message = 'Property %s in the object %s should not be a list' %\
                    (object_property, i_id)
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

        # Check if functional property w.r.t. current class, if so add as-is
        # if not cast to list and append (if not list)
        # See: http://bit.ly/2YY8rzz (search for 'FunctionalProperty')
        if config.data_properties[data_property].is_functional_for(config.
            ont_classes[i_type]):
            if type(candidate_property) is list:
                message = 'Property %s in the object %s should not be a list' %\
                    (data_property, i_id)
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

        for descr in descr_obj:
            if 'hasPriority' in descr.keys():
                priority = descr['hasPriority']
            else:
                priority = 0
            ret_obj.append(config.ont.Description(
                uuid4(),
                namespace=config.namespace,
                hasPriority=[priority],
                hasText=descr['hasText']
            ))
        
        # Check if functional property w.r.t. current class, if so add as-is
        # if not cast to list and append (if not list)
        # See: http://bit.ly/2YY8rzz (search for 'FunctionalProperty')
        if config.ont.hasDescription.is_functional_for(config
            .ont_classes[obj_type]):
            if isList:
                message = 'Description in the object %s should not be a list' %\
                    (obj_id)
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
            message = 'Entity %s referenced before assignment in %s' %\
                (search_id, obj_id)
            logging.error(message)
            raise ReferenceError(message)
        
        return res[0]
