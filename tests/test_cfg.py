class TestConfig():
    """Class to store test configuration variables.
    """
    
    # Namespace to be used in the ontology 
    namespace = 'http://precis.rukmal.me/ontology/musk'

    sample_json_data = 'data/sample.json'  # Sample JSON (Musk resume)
    sample_rdf_data = 'data/sample.rdf'  # Sample RDF (Musk resume)
    test_save_location = 'data/test.rdf'  # Location to save test file

    # Templating tests
    template_folder = 'templates/'
    template_cv = 'templates/curriculum_vitae'
    template_prefs = 'data/sample_cv_prefs.yml'
