.PHONY: linters
linters: black flake8 mypy isort bandit ## checks code style

.PHONY: flake8
flake8: ## checks codebase with flake8
	$(RUN_ENVIRONMENT) flake8 charts crypto_analyzer tests

.PHONY: mypy
mypy: ## checks typehints
	$(RUN_ENVIRONMENT) mypy charts crypto_analyzer tests

.PHONY: isort
isort: ## checks if imports are sorted correctly
	$(RUN_ENVIRONMENT) isort -c charts crypto_analyzer tests

.PHONY: isort_fix
isort_fix: ## fixes imports
	$(RUN_ENVIRONMENT) isort charts crypto_analyzer tests

.PHONY: bandit
bandit: ## checks if there aren't any secrets in code
	$(RUN_ENVIRONMENT) bandit -r src

.PHONY: black
black: ## check codebase with black
	$(RUN_ENVIRONMENT) black --check --diff --line-length 100 .

.PHONY: black_fix
black_fix: ## fixes code style
	$(RUN_ENVIRONMENT) black --line-length 100 charts crypto_analyzer tests
