SHELL:=/usr/bin/env bash

.PHONY: lint
lint:
	poetry run mypy core main.py
	poetry run flake8 .
	poetry run autopep8 -r . --diff --exit-code
	poetry run lint-imports
	poetry run doc8 -q docs

.PHONY: package
package:
	poetry run poetry check
	poetry run pip check