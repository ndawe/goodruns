# simple makefile to simplify repetitive build env management tasks under posix

PYTHON ?= python
NOSETESTS ?= nosetests

all: clean inplace test

clean-pyc:
	find . -name "*.pyc" -exec rm {} \;

clean-build:
	rm -rf build

clean-distribute:
	rm -f distribute-*.egg
	rm -f distribute-*.tar.gz

clean: clean-build clean-pyc clean-distribute

in: inplace # just a shortcut
inplace:
	$(PYTHON) setup.py build_ext -i

install:
	$(PYTHON) setup.py install

install-user:
	$(PYTHON) setup.py install --user

sdist: clean
	$(PYTHON) setup.py sdist

register:
	$(PYTHON) setup.py register

upload: clean
	$(PYTHON) setup.py sdist upload

test-code: in
	$(NOSETESTS) -v -s goodruns --nologcapture

test-doc:
	$(NOSETESTS) -s --with-doctest --doctest-tests --doctest-extension=rst \
	--doctest-extension=inc --doctest-fixtures=_fixture docs/

test-coverage:
	rm -rf coverage .coverage
	$(NOSETESTS) -s --with-coverage --cover-html --cover-html-dir=coverage \
	--cover-package=goodruns goodruns

test: test-code test-doc

trailing-spaces:
	find goodruns -name "*.py" | xargs perl -pi -e 's/[ \t]*$$//'

ctags:
	# make tags for symbol based navigation in emacs and vim
	# Install with: sudo apt-get install exuberant-ctags
	$(CTAGS) -R *

doc: inplace
	make -C docs/ html

update-distribute:
	curl -O http://python-distribute.org/distribute_setup.py

check-rst:
	python setup.py --long-description | rst2html.py > __output.html
	rm -f __output.html
