# Script to build the sample RDF file from the sample JSON file

from context import precis
from test_cfg import TestConfig
import os

def buildSampleRDF():
    # Opening json file
    with open(TestConfig.sample_json_data, "r") as f:
        # Instantiating loader
        loader = precis.Loader(ingest_file=f, namespace=TestConfig.namespace)

    # Saving completed ontology to file
    loader.saveToFile(save_location=TestConfig.sample_rdf_data)


if __name__ == '__main__':
    buildSampleRDF()
