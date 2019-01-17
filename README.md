# *Précis*
> Refreshingly non-redundant Resumes

## Goals

- Have single data repository for all resume data (i.e. jobs, start dates, descriptions, etc.)
    - Why: To avoid spending a stupid amount of time regurgitating the same shit over and over again when creating a new resume
- Add metadata to data file, for things like languages/frameworks used, etc. This can be capitalized later on if you choose to port to a RDF-based representation of stuff, and for fancy templating things on your new resume
- Build templating engine with Jinja and LaTeX to render specifically styled resumes on the fly.
    - Need to think about how different descriptions and shit fit into this; single JSON or different ones?
    - Perhaps a system of overrides would work well here (like config vars in ZocialGPA stuff)
- Create utility to render this shit on the fly, with the ability to select/leave out shit from the data repository on the fly (i.e. having tech publications take up space on a resume for a pure finance job doesn't make too much sense). This utility will probably have a set of arguments similar to:
    - Data file, with descriptions, start/end dates, etc.
    - Override settings, files
        - i.e. have a file with the same structure, but different descriptions or something for some specific bullshit you need; an example of this would be having a more finance-oriented description for Hyperloop in a single JSON file which can override the default option
    - Which template to use
        - Can have multiple here; for example, one for IAQF, one CV, etc.
        - Offload logic of selecting specific template items to the Jinja template; this make a lot more sense from an OOP perspective


## Structure

```
- templates/
    |- _template.tex
    |- iaqf_template.tex
    |- cv_template.tex
    |- resume_template.tex
- data/
    |- _template.json (important)
    |- main.json (main data goes here; rest are specific files)
    |- finance.json
- 
```

## TODO - Plan

- Start by creating the data repository; create `_template.json` while creating the actual file for easier override creation
    - 
