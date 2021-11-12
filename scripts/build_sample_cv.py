# Script to build the sample RDF file from the sample JSON file

import os
from context import precis
from owlready2 import default_world, get_ontology
from test_cfg import TestConfig


def buildSampleCV():
    # Load resume template
    cv_template = precis.templating.PrecisTemplate(
        template_folder=os.path.join(precis.config.templates_folder, "curriculum_vitae/")
    )

    # Load user ontology
    user_ont = get_ontology(TestConfig.sample_rdf_data).load()

    # Casting to RDFLib graph
    user_graph = default_world.as_rdflib_graph()

    # Loading user preferences (for template)
    with open(TestConfig.template_prefs) as cv_prefs:
        driver = precis.templating.TemplateDriver(
            template=cv_template,
            user_ont=user_ont,
            user_graph=user_graph,
            user_prefs=cv_prefs
        )

    with open(TestConfig.template_cv_out, "w") as f:
        f.write(driver.buildTemplate())


if __name__ == '__main__':
    buildSampleCV()
