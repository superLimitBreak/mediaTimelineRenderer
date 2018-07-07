ENV=_env
PYTHON_VERSION:=3.6
DEPENDENCIES_PYTHON:=mediaTimelineRenderer.pip
PYTHON:=$(ENV)/bin/python$(PYTHON_VERSION)
PIP:=$(ENV)/bin/pip$(PYTHON_VERSION)
PYTEST:=$(ENV)/bin/py.test

help:
	#
	# install
	# run
	# test
	# clean


.PHONY: install
install: $(ENV) upgrade_pip test

$(ENV):
	virtualenv --no-site-packages -p python$(PYTHON_VERSION) $(ENV)

.PHONY: upgrade_pip
upgrade_pip:
	$(PIP) install --upgrade pip ; $(PIP) install --upgrade -r $(DEPENDENCIES_PYTHON)

.PHONY: run
run:
	$(PYTHON) mediaTimelineRenderer.py

.PHONY: test
	$(PYTEST) .

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV) ./


# Clean ------------------------------------------------------------------------

.PHONY: clean_cache
clean_cache:
	find . -iname *.pyc -delete
	find . -iname __pycache__ -delete
	find . -iname .cache -delete

.PHONY: clean
clean: clean_cache
	rm -rf $(ENV)
	#rm -rf $(CONFIG)
