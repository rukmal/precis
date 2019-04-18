from owlready2.namespace import Namespace, Ontology


class config():

    # Precis ontology versions
    __ont_sources = {
        'local': './precis_ontology.rdf',
        '1.0.0': 'https://github.com/rukmal/precis/releases/download/1.0.0/precis_ontology.rdf',
        '1.0.1': 'https://github.com/rukmal/precis/releases/download/1.0.1/precis_ontology.rdf',
        '1.1.0': 'https://github.com/rukmal/precis/releases/download/1.1.0/precis_ontology.rdf',
        '1.1.1': 'https://github.com/rukmal/precis/releases/download/1.1.1/precis_ontology.rdf',
        '1.2.0': 'https://github.com/rukmal/precis/releases/download/1.2.0/precis_ontology.rdf',
        '1.2.1': 'https://github.com/rukmal/precis/releases/download/1.2.1/precis_ontology.rdf',
        '1.3.0': 'https://github.com/rukmal/precis/releases/download/1.3.0/precis_ontology.rdf',
        '1.4.0': 'https://github.com/rukmal/precis/releases/download/1.4.0/precis_ontology.rdf',
        '1.5.0': 'https://github.com/rukmal/precis/releases/download/1.5.0/precis_ontology.rdf'
    }

    # Ontology source URL
    # Currently configured for use with Precis Ontology 1.5.0
    ont_source = __ont_sources['1.5.0']

    # NOTE: The following are set to empty here to help with linting; they
    #       are set at runtime when Precis is initialized.
    
    ont: Ontology = None  # Ontology
    ont_base_iri: str = None  # Ontology base IRI
    object_properties: dict = {}  # Object property map
    data_properties: dict = {}  # Data property map
    ont_classes: dict = {}  # Ontology class map
    namespace: Namespace = None  # Namespace for the current ontology


    # Templating Stuff

    # Template folder (relative to top-level package import)
    templates_folder = './templates'

    # Template file names
    template_files = {
        'config': 'template_config.yml',
        'template': 'template.tex.j2'
    }

    # Required template configuration fields
    template_config_required = ['full_name', 'description', 'author',
                                'required_input', 'required_classes']
