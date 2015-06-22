# simple makefile to simplify repetitive build env management tasks under posix

PYTHON := $(shell which python)                                                 
NOSETESTS := $(shell which nosetests)

all: clean inplace test

clean-pyc:
	@find . -name "*.pyc" -exec rm {} \;

clean-build:
	@rm -rf build

clean: clean-build clean-pyc

in: inplace # just a shortcut
inplace:
	@$(PYTHON) setup.py build_ext -i

install:
	@$(PYTHON) setup.py install

install-user:
	@$(PYTHON) setup.py install --user

sdist: clean
	@$(PYTHON) setup.py sdist

register:
	@$(PYTHON) setup.py register

upload: clean
	@$(PYTHON) setup.py sdist upload

test-code: in
	@$(NOSETESTS) -v -s goodruns --nologcapture

test-doc:
	@$(NOSETESTS) -s --with-doctest --doctest-tests --doctest-extension=rst \
	--doctest-extension=inc --doctest-fixtures=_fixture docs/

test-coverage:
	@rm -rf coverage .coverage
	@$(NOSETESTS) -s -v --with-coverage \
		--cover-erase --cover-branches \
		--cover-html --cover-html-dir=coverage \
		--cover-package=goodruns goodruns

test: test-code test-doc

trailing-spaces:
	@find goodruns -name "*.py" | xargs perl -pi -e 's/[ \t]*$$//'

doc: inplace
	@make -C docs/ html

check-rst:
	@$(PYTHON) setup.py --long-description | rst2html.py > __output.html
	@rm -f __output.html

gh-pages: doc
	@./ghp-import -m "update docs" -r origin -f -p docs/_build/html/
