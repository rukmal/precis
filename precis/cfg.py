class config:

    # Precis ontology versions
    __ont_sources = {
        '1.0.0': 'https://github.com/rukmal/precis/releases/download/1.0.0/precis_ontology.rdf'
    }

    # Ontology source URL
    # Currently configured for use with Precis Ontology 1.0.0
    ont_source = __ont_sources['1.0.0']

    # NOTE: The following are set to 'None' here to help with linting; they
    #       are set at runtime when Precis is initialized.
    
    ont = None  # Ontology
    obj_properties = None  # Object property list
