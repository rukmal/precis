from .template import PrecisTemplate
from .. import OntQuery
from ..cfg import config

from io import TextIOWrapper
from owlready2.namespace import Ontology
from rdflib import Graph
from yaml import load as yaml_load, SafeLoader
from yaml.parser import ParserError
import logging


class TemplateDriver():
    """This module encapsulated functionality to ingest user data, user template
    preferences, a template, and to render the template based on that data.

    TemplateDriver ingests user template preferences, and checks them for
    validity, both against the content of the supplied user data ontology, and
    the content of the template configuration.
    """
    
    def __init__(self, template: PrecisTemplate, user_ont: Ontology,
                 user_graph: Graph, user_prefs: TextIOWrapper):
        """TemplateDriver initialization method. Validates user preferences
        against the supplied ontology, and against the template configuration.

        This initialization method also builds user data to be passed to the
        template, but does not start the build process. This data is constructed
        using restrictions from the user preferences, and only required classes
        from the template configuraion. Intelligent logging and error messages
        pinpoint errors in user preferences for easy debugging.
        
        Arguments:
            template {Template} -- Template to be rendered.
            user_ont {Ontology} -- User data ontology.
            user_graph {Graph} -- RDFLib graph representation of the ontology.
            user_prefs {TextIOWrapper} -- User template preferences file.
    
        Raises:
            AttributeError -- Raised when a attribute required by the template
                              configuration is missing from the user prefs, or
                              if invalid class names are used.
            KeyError -- Raised when an invalid class type or class ID is used in
                        preferences that does not exist in the user ontology.
            ParserError -- Raised when the user preferences has malformed
                           YAML syntax.
            ValueError -- Raised when an invalid ordering scheme is specified.
        """
        
        # Binding class variables
        self.template = template

        # Parsing user preferences, saving to class variable
        try:
            self.user_prefs = yaml_load(stream=user_prefs, Loader=SafeLoader)
            self.user_prefs_attrs = set(self.user_prefs.keys())
        except ParserError:
            message = 'User preferences file {0} is malformed'.format(
                user_prefs.name)
            logging.error(message)
            raise

        # Checking all attributes required by the template are present in
        # user configuration file
        if not self.template.getRequiredInput().issubset(self.user_prefs_attrs):
            message = 'Required user preferences {0} are missing'.format(
                self.template.getRequiredInput().difference(
                self.user_prefs_attrs))
            logging.error(message)
            raise AttributeError(message)
        
        logging.debug('User prefs validated with all required keys present')
        
        # Building template data
        self.template_data = dict()

        # Ensuring order overrides and item overrides are valid
        order_overrides = self.__getOrderOverrides()
        item_overrides = self.__getItemOverrides()

        # Instantiating query agent
        self.query = OntQuery(ont=user_ont, graph=user_graph)

        # Dictionary to store user data
        self.user_data = dict()

        # Extracting template data from the ontology
        for ont_class in self.template.getRequiredClasses():
            # Isolating order override (if any)
            if ont_class in order_overrides.keys():
                order = order_overrides[ont_class]
            else:
                order = None

            # Getting all of type 'ont_class', with order restrictions
            class_invds = self.query.getAllOfType(c_type=ont_class, order=order)

            # Apply item overrides (if they exist for current `ont_class`)
            if ont_class in item_overrides.keys():
                # Keep if the individual ID is in item overrides
                # Note: This preserves ordering from retrieval function
                class_invds = [i for i in class_invds if i['$id']
                    in item_overrides[ont_class]]

            logging.debug('Extracted {0} individuals of class {1} for template'\
                .format(len(class_invds), ont_class))

            # Appending to user data dictionary
            self.user_data[ont_class] = class_invds
        
        # Appending required fields from user preferences to user data
        for field in self.template.getRequiredInput():
            self.user_data[field] = self.user_prefs[field]

        logging.info('Successfully built user data object for template\
            rendering with {0} fields'.format(len(self.user_data.keys())))

    def buildTemplate(self) -> str:
        """Function to build the template, using data constructed from the
        ontology and user preferences.
        
        Returns:
            str -- Built template.
        """

        return self.template.renderTemplate(render_data=self.user_data)

    def __getItemOverrides(self) -> dict:
        """Function to get specific item overrides, in a dictionary of the form
        {OntologyClass: [item_id_1, item_id_2, ...]}. This function also
        validates that listed IDs are valid, and that they exist in the ontology
        and are of the correct type.
        
        Raises:
            KeyError -- Raised when an incorrect class type or class ID is used.
            ValueError -- Raised when inclusion and exclusion type item
                          overrides are mixed.
        
        Returns:
            dict -- Dictionary of item overrides.
        """

        # Only proceed if item overrides are specified
        if 'item_overrides' not in self.user_prefs_attrs:
            return {}

        for item_type in self.user_prefs['item_overrides']:
            # Getting IDs of individuals of the given type (from the key)
            try:
                indv_ids = set([i.name for i in
                    config.ont_classes[item_type].instances()])
            except KeyError:
                message = 'Item override type {0} in item overrides not valid'.\
                    format(item_type)
                logging.error(item_type)
                raise
            
            
            # Building list to check negation flag
            negation_flag = [i[0] == '!'
                for i in self.user_prefs['item_overrides'][item_type]]
            
            # Following if statement handles each of the cases where (1) all are
            # negation IDs, (2) negation/inclusion is mixed raise error, or (3)
            # all inclusion IDs

            if all(negation_flag):
                # All Negation
                # Building set of IDs to be removed (i.e. removing '!')
                negate_ids = set([i[1:]
                    for i in self.user_prefs['item_overrides'][item_type]])
                if negate_ids.issubset(indv_ids):
                    # Subtracting negation IDs from all IDs to build list of IDs
                    # to include
                    include_ids = indv_ids.difference(negate_ids)
                    # Casting to list and assigning to dictionary value
                    self.user_prefs['item_overrides'][item_type] = \
                        list(include_ids)
                    # Skip rest, continue
                    continue
                # Not all negation IDs are not valid, raise error
                message = 'Item negation ID overrides {0} for type {1} are not\
                    valid.'.format(negate_ids, item_type)
                logging.error(message)
                raise KeyError(message)
            elif any(negation_flag) and not all(negation_flag):
                # Mixed; both inclusion and negation are used
                # Raise error
                message = 'Both negation and inclusion item overrides are used\
                    for class {0}'.format(item_type)
                logging.error(message)
                raise ValueError(message)
            else:
                # All Inclusion
                # Check if all IDs are valid, if so continue
                if set(self.user_prefs['item_overrides'][item_type]).issubset(
                    indv_ids):
                    continue
                # If not valid, raise error
                message = 'Item ID overrides {0} for type {1} are not valid'.\
                    format(set(self.user_prefs['item_overrides'][item_type])
                    .difference(indv_ids), item_type)
                logging.error(message)
                raise KeyError(message)

        return self.user_prefs['item_overrides']

    def __getOrderOverrides(self) -> dict:
        """Function to get order overrides for each type. Evaluates that the
        ordering type specified is valid, and returns a dictionary of the form
        {OntologyClass: OrderType} for each override specified in the
        user preferences.
        
        Raises:
            AttributeError -- Raised if an invalid class name is specified.
            ValueError -- Raised if an invalid order override is specified.
        
        Returns:
            dict -- Dictionary of order overrides.
        """

        # Only proceed if order overrides are specified
        if 'order_overrides' not in self.user_prefs_attrs:
            return {}
        
        # Isolating invalid classes
        invalid_classes = set(self.user_prefs['order_overrides']).difference(
            set(config.ont_classes.keys()))

        # Raise exception if there are any invalid classes
        if len(invalid_classes) > 0:
            message = 'Order override class {0} is not valid'.format(
                invalid_classes)
            logging.error(message)
            raise AttributeError(message)

        # Iterate through order overrides, and ensure they are valid
        for order_override in self.user_prefs['order_overrides']:
            override_type = self.user_prefs['order_overrides'][order_override]
            if override_type not in config.valid_order_options:
                message = 'Invalid order override option {0} for class {1}'.\
                    format(override_type, order_override)
                logging.error(message)
                raise ValueError(message)

        return self.user_prefs['order_overrides']
