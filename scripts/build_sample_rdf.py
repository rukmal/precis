# Script to build the sample RDF file from the sample JSON file

from context import precis
from tests.test_cfg import TestConfig

def buildSampleRDF():
    # Opening json file
    f = open(TestConfig.sample_json_data, 'r')

    # Instantiating loader
    loader = precis.Loader(ingest_file=f, namespace=TestConfig.namespace)

    # Saving completed ontology to file
    loader.saveToFile(save_location=TestConfig.sample_rdf_data)


if __name__ == '__main__':
    buildSampleRDF()
