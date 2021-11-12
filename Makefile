.DEFAULT_GOAL := help


# Base build recipes
#####################

.PHONY: build_cv_from_rdf
build_cv_from_rdf: ## Build CV LaTeX and PDF from the sample data RDF file
	cd scripts && python build_sample_cv.py
	cd data && pdflatex cv.tex

.PHONY: build_rdf_from_json
build_rdf_from_json: ## Build RDF from the sample data JSON file
	cd scripts && python build_sample_rdf.py


# Compound build recipes
########################

.PHONY: build_cv_from_json
build_cv_from_json: ## Build CV LaTeX and PDF from the sample data JSON
	$(MAKE) build_rdf_from_json
	$(MAKE) build_cv_from_rdf

# Util
#######

.PHONY: help
help: # See: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
