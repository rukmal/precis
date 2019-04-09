from owlready2.namespace import Namespace, Ontology


class config:

    # Precis ontology versions
    __ont_sources = {
        '1.0.0': 'https://github.com/rukmal/precis/releases/download/1.0.0/precis_ontology.rdf'
    }

    # Ontology source URL
    # Currently configured for use with Precis Ontology 1.0.0
    ont_source = __ont_sources['1.0.0']

    # NOTE: The following are set to empty here to help with linting; they
    #       are set at runtime when Precis is initialized.
    
    ont: Ontology = None  # Ontology
    obj_properties: list = []  # Object property list
    data_properties: list = []  # Data property list
    ont_classes: dict = {}  # Ontology class constructors
    namespace: Namespace = None  # Namespace for the current ontology
