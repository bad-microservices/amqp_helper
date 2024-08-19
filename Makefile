checkfiles = amqp_helper/ doc/

help:
	@echo "amqp_helper Makefile"
	@echo "usage: make <target>"
	@echo "Targets:"
	@echo "    - doc       Build the documentation"
	@echo "    - package   Build amqp_helper as package"

deps:
	pipenv --python /usr/bin/python3 install --dev

doc: deps
	rm -fR ./_build
	cp ./CHANGELOG.rst ./doc/
	pipenv --python /usr/bin/python3 run sphinx-build -M html doc _build
	rm ./doc/CHANGELOG.rst

package: deps
	rm -fR dist/
	pipenv run python -m build
