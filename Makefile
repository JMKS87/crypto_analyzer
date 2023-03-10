RUN_ENVIRONMENT = docker-compose run -e CUSTOM_COMPILE_COMMAND="make requirements" --rm app

include makefiles/clean.mk
include makefiles/django.mk
include makefiles/docker-compose.mk
include makefiles/docker-repo.mk
include makefiles/dotenv.mk
include makefiles/help.mk
include makefiles/linters.mk
include makefiles/requirements.mk
include makefiles/tests.mk

.PHONY: dev-env
dev-env:  ## chain of commands to produce complete developer environment
	$(MAKE) dotenv
	git secret reveal
	$(MAKE) build
	$(MAKE) manage.py CMD=migrate
	$(MAKE) manage.py CMD=collectstatic
