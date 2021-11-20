.PHONY: requirements
requirements: ## compiles all the requirements files
	$(RUN_ENVIRONMENT) pip-compile -o requirements/requirements.txt requirements/requirements.in

.PHONY: update_requirements
update_requirements: ## updates all the requirements
	$(RUN_ENVIRONMENT) pip-compile --upgrade -o requirements/requirements.txt requirements/requirements.in
