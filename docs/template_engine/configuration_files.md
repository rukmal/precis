# Template Instance Configuration Files

In addition to inherent template configuration (in the relevant `*.tex.j2` file for a given template), an instance configuration file to be used at render time is required from the user.

The requirements of this instance configuration file for a given template is outlined in the `template_config.yml` file , in the same folder as the template file (`*.tex.j2`) for a given template.

For the rest of this tutorial, we outline the template configuration file of the [*Curriculum Vitae* template](https://github.com/rukmal/precis/tree/master/templates/curriculum_vitae).


## Required Input

For a given template to function correctly, it may specify a set of *required input*. This required input is outlined in the template configuration file discussed above. The required input is listed in a YAML file, supplied to Precis at rendering time as an additional argument to the template driver.

Continuing with the *Curriculum Vitae* example discussed above, a basic instance configuration file can be created (reproduced below). Note that - as detailed in the template configuration file - a total of 8 required fields are outlined; `full_name`, `address_line_1`, `address_city_state`, `address_zip`, `address_country`, `phone`, `email`, and `website`.

```yaml
full_name: 'Elon Musk'
address_line_1: '3500 Deer Creek Road'
address_city_state: 'Palo Alto, CA'
address_zip: '94304'
address_country: 'USA'
phone: '(800) 613-8840'
email: 'elonmuskoffice@teslamotors.com'
website: 'tesla.com'
```


## Content Overrides

To best capture the diverse formats of various resume designs and templates, Precis provides a set of built-in functionality to control the ordering and placement of items in the user's Precis knowledge graph when building a resume.

These overrides are divided into two main categories:

- *Order Overrides*: Overrides that affect the ordering of precis data.
- *Item Overrides*: Overrides that affect specific elements of the precis data.

### Order Overrides

Order overrides can be used to specify an ordering scheme for a given class in the precis knowledge graph. The supposed overrides are:

- `chron_A`: Ascending chronological order.
- `chron_D`: Descending chronological order.
- `alphabetical_A`: Ascending alphabetical order.
- `alphabetical_D`: Descending alphabetical order.

These overrides must be included as key-value pairs, with the key being the precis concept class to which the order applies, and the value being the desired order. For example:

```yaml
full_name: 'Elon Musk'
.
.
.
order_overrides:
  WorkExperience: 'chron_D'
  Award: 'chron_A'
  SkillGroup: 'alphabetical_A'
  KnowledgeArea: 'alphabetical_D'
```

### Item Overrides

Item overrides can be used to supply specific IDs of elements in the precis knowledge graph that will or will not be included in the rendered output. These overrides support two specific types of use:

- *Inclusion Override*: List of specific IDs to include.
- *Exclusion Override*: List of specific IDs to exclude.

Note that the usage of each these types of item overrides are mutually exclusive. That is, they cannot be used in conjunction with each other. Also note that the default behavior of the template engine - in the absence of any provided inclusion item override - is to include all applicable items in the knowledge graph.

This default behavior means that the mutual exclusivity of each of these overrides does not limit their functionality, as specific lists of items (with specific IDs; *inclusion override*) can be included, as well as all items with the exception of a few (with specific IDs; *exclusion override*).

The *inclusion override* is used to specify a list of specific IDs to include (as demonstrated with the `Degree` concept below), and the *exclusion override* is used to list IDs to be excluded (as demonstrated with the `ActivityType` concept below). They are differentiated by using a '!' character before the ID for exclusion, and none for inclusion. See the example below for more details:

```yaml
full_name: 'Elon Musk'
.
.
.
item_overrides:
  Degree:
    - 'degree_bs_physics'
    - 'degree_bs_econ'
  ActivityType:
    - '!ac_type:debauchery'
```

## Full Example

The following is the full example of the template instance configuration file discussed in this example. Note that this is the [same file](https://github.com/rukmal/precis/blob/master/data/sample_cv_prefs.yml) as the sample configuration file used in the quickstart guide.

```yaml
full_name: 'Elon Musk'
address_line_1: '3500 Deer Creek Road'
address_city_state: 'Palo Alto, CA'
address_zip: '94304'
address_country: 'USA'
phone: '(800) 613-8840'
email: 'elonmuskoffice@teslamotors.com'
website: 'tesla.com'
order_overrides:
  WorkExperience: 'chron_D'
  Award: 'chron_A'
  SkillGroup: 'alphabetical_A'
  KnowledgeArea: 'alphabetical_D'
item_overrides:
  Degree:
    - 'degree_bs_physics'
    - 'degree_bs_econ'
  ActivityType:
    - '!ac_type:debauchery'
```
