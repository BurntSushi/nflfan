REMOTE=Geils:~/www/burntsushi.net/public_html/stuff/nflfan/

all:
	@echo "Specify a target."

pypi: docs longdesc.rst
	sudo python2 setup.py register sdist bdist_wininst upload

docs:
	pdoc --html --html-dir ./doc --overwrite ./nflfan

longdesc.rst: nflfan/__init__.py docstring
	pandoc -f markdown -t rst -o longdesc.rst docstring
	rm -f docstring

docstring: nflfan/__init__.py
	./scripts/extract-docstring > docstring

dev-install:
	[[ -n "$$VIRTUAL_ENV" ]] || exit
	rm -rf ./dist
	python setup.py sdist
	pip install -U dist/*.tar.gz

pep8:
	pep8-python2 nflfan/*.py

push:
	git push origin master
	git push github master
