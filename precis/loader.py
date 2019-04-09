from .cfg import config

from collections import OrderedDict
from owlready2.entity import ThingClass
from uuid import uuid4
from typing import Union
import json
import logging


class Loader():

    def __init__(self, ingest_file: str, namespace: str=None):
        # Initialize with file name
        # Iterate through (it will be an array @ top level)
        # Correctly call class constructors (depending on $type)
        
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
            raw = json.load(f, object_pairs_hook=OrderedDict)
        except Exception:
            print('file not found.')

        for instance in raw:
            # Creating ontology class from instance
            self.__processInstance(candidate_object=instance)
        
        logging.info('Success! Added %i individuals to the Precis ontology.' %\
            (len(list(config.ont.individuals()))))

    def __processInstance(self, candidate_object: dict) -> ThingClass:
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

        # Creating instance by calling class constructor
        return config.ont_classes[individual_type](
            individual_id,
            namespace=config.namespace,
            **new_individual
        )

    def __handleObjectProperty(self, object_property: str, i_type: str,
        i_id: str, candidate_obj: object) -> Union[list, ThingClass]:
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
                raise Exception(message)
            return ret_obj[0]
        else:
            return ret_obj

    def __handleDataProperty(self, data_property: str, i_type: str, i_id: str,
        candidate_property: object) -> Union[int, str, float, list]:
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
                raise Exception(message)
            return ret_obj[0]
        else:
            return ret_obj

    def __findInOntology(self, search_id: str, obj_id: str) -> list:
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
