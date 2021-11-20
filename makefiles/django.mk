MANAGE_PY = python /app/manage.py

.PHONY: manage.py
manage.py:  ## runs chosen command in manage.py; usage: make manage.py CMD=command
	$(RUN_ENVIRONMENT) $(MANAGE_PY) $(CMD)
