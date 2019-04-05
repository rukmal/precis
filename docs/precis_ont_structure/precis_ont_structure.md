# Precis Ontology Structure

This document describes the structure of the Precis ontology. Note that this information is **not** necessary to use the Precis toolkit. It is here primarily for reference, and for anyone that wants to understand how the ontology is structured at a deeper level.

> **Note 1:** This document also has JSON schema descriptions (not a complete [JSON Schema](https://json-schema.org/) for now...) for each of the Concepts outlined in the Ontology. This information is not necessary to understand the Precis ontology structure, and is provided for reference purposes.

> **Note 2:** Unless otherwise stated, the `$id` field in JSON schema descriptions is optional. If left blank, the precis toolkit will auto-generate an ID on JSON ingestion. This will also mean that the instance in question will be un-referenceable, as a random ID will be generated upon ingestion.

## Overall Structure


<div style="text-align: center">
    <img src="assets/protege_classes.png">
</div>

## Concepts (i.e. *Classes*)
This subsection describes each of the top-level concepts (or *classes*) in the Ontology. The heading level corresponds to the concept's position in the ontology class structure.

### Accolade

This concept is an umbrella class for anything that can be construed as an accolade of some sort. In the case of a traditional portfolio, this would be something that is classified as an award or certification; hence the current subclasses.

No concepts should be instantiated as an *Accolade*, but rather as one of its subclasses; *Award* or *Certification*. Thus, there is no construction information for this umbrella class.

#### Award

```json
{
    "$id": "User-defined ID",
    "inMonth": "Month the award was received",
    "externalResource": ["List of external resources ("],
    "affiliatedWith": "ID of Degree/WorkExperience instance that this award is affiliated with",
    "hasDescription": ["List of Description instances corresponding to this award"],
    "hasMedia": ["List of media (URLs) for media related to this instance"],
    "inYear": "Year the award was received",
    "hasName": "Display name for the award",
    "relatedTo": "Related instances; can be anything in Precis"
}
```

This concept describes what may traditionally be described as an "award".

For example, this class would encapsulate something like "Dean's List", or "1st Place in Hackathon X". Note that in the case of the second example, it would be related to a "Hackathon", which would be linked using the `relatedTo` object property.

#### Certification

```json
{
    "$id": "User-defined ID",
    "inMonth": "Month the certification was received",
    "externalResource": ["List of external resources ("],
    "affiliatedWith": "ID of Degree/WorkExperience instance that this certification is affiliated with",
    "hasDescription": ["List of Description instances corresponding to this certification"],
    "hasMedia": ["List of media (URLs) for media related to this instance"],
    "inYear": "Year the certification was received",
    "hasName": "Display name for the certification",
    "relatedTo": "Related instances; can be anything in Precis"
}
```

This concept describes what may traditionally be described as a "certification".

For example, this class would encapsulate something like "CPR Certification", or "Bloomberg Market Concepts Certificate". Note that in the case of the second example, it would be related to a *Course*, *Degree* or *Organization*, which would be linked using the `relatedTo` property.

### ActivityType

```json
{
    "$id": "User-defined ID",
    "inMonth": "Month the certification was received",
    "externalResource": ["List of external resources ("],
    "hasDescription": ["List of Description instances corresponding to this certification"],
    "hasMedia": ["List of media (URLs) for media related to this instance"],
    "inYear": "Year the certification was received",
    "hasName": "Display name for the certification",
    "relatedTo": "Related instances; can be anything in Precis"
}
```

This concept would describe a "type" of Activity.

That is, it should be treated as an umbrella class to describe a set of activities that can be relegated to a specific "type". Examples of this would include a "Hackathon" *ActivityType*, which be a superclass to many individual instances of Hackathons.

#### Activity

This concept describes a specific *Activity*.

This should be an instance of a specific *ActivityType*. That is, it would be a specific Hackathon (which would in turn be a subclass of the "Hackathon" *ActivityType*).


### Course


### Degree


### Description


### KnowledgeArea

#### Subject


### Organization


### Portfolio

#### Project

#### Publication

#### Talk


### SkillGroup

#### Skill


### WorkExperience

## Object Properties (i.e. *Relationships*)

- 
