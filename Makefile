checkfiles = jwt_helper/ doc/

help:
	@echo "jwt_helper Makefile"
	@echo "usage: make <target>"
	@echo "Targets:"
	@echo "    - doc       Build the documentation"
	@echo "    - package   Build jwt_helper as package"

deps:
	pipenv --python /usr/bin/python3 install --dev

doc: deps
	rm -fR ./_build
	cp ./CHANGELOG.rst ./doc/
	pipenv run sphinx-build -M html doc _build
	rm ./doc/CHANGELOG.rst

package: deps
	rm -fR dist/
	pipenv --python /usr/bin/python3 run python -m build
