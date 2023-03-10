MANAGE_PY = python /app/manage.py
MANAGE_PY_WIN = python manage.py

.PHONY: manage.py
manage.py:  ## runs chosen command in manage.py; usage: make manage.py CMD=command
	$(RUN_ENVIRONMENT) $(MANAGE_PY) $(CMD)

.PHONY: manage.py.win
manage.py.win:  ## runs chosen command in manage.py; usage: make manage.py.win CMD=command
	$(RUN_ENVIRONMENT) $(MANAGE_PY_WIN) $(CMD)
