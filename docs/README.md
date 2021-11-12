<p align="center">
    <h2><a href="https://precis.rukmal.me/ontology">Click Here for Precis Ontology Specification</a></h2>
</p>

## Overview

Precis is (primarily) an [Ontology for modeling personal professional metadata](https://precis.rukmal.me/ontology). That is, it provides functionality to track metadata such as Degrees, Courses, Portfolio Items (Publications, Projects, Talks), Work Experience, etc.

In addition to the Precis Ontology modeling personal metadata, the Precis toolkit extends this Ontology by providing additional functionality, specifically:

- JSON Loading tool, to ingest data into the Precis Ontology (outputs RDF)
- Simple Pythonic Query API for information stored in the Ontology
- Extensible templating engine (for CV/Resume generation), built with [Jinja](http://jinja.pocoo.org/docs/2.10/templates/)

Each of these functions are illustrated below in the Quickstart Guide.

**Note: This document is still under construction**

## Advanced Documentation

This section is advanced documentation for specific topics in Precis.

### Template Engine

- [Template Instance Configuration Files](template_engine/configuration_files.md)

A description of the underlying Precis ontology. Details each of the individual concepts, object properties and data properties comprising the ontology.

## Local Development

The [`Makefile`](../Makefile) contains useful recipes for local development.

```bash
$ make help

build_cv_from_json             Build CV LaTeX and PDF from the sample data JSON
build_cv_from_rdf              Build CV LaTeX and PDF from the sample data RDF file
build_rdf_from_json            Build RDF from the sample data JSON file
```

### Archive

**Note**: This is mostly out of date, but the broad strokes are accurate. Preserved for posterity.

- [Precis Ontology Structure](precis_ont_structure/precis_ont_structure.md)


## Acknowledgements

- [Garijo, Daniel. "WIDOCO: a wizard for documenting ontologies." International Semantic Web Conference. Springer, Cham, 2017.](https://github.com/dgarijo/Widoco)
- [Lamy JB. Owlready: Ontology-oriented programming in Python with automatic classification and high level constructs for biomedical ontologies. Artificial Intelligence In Medicine 2017;80:11-28](https://bitbucket.org/jibalamy/owlready2)


## Contact

[Rukmal Weerawarana](http://rukmal.me)
