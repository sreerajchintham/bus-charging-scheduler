.PHONY: install test

PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest -v
