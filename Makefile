setup:
	python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/bin/activate

clean:
	scripts/build.sh -c

test:
	scripts/run_tests.sh

debug:
	scripts/build.sh -cd

build:
	scripts/build.sh

publish:
	scripts/publish.sh

lint:
	pylint *.py

black:
	black .

mypy:
	mypy --disallow-untyped-defs .

list:
	@grep '^[^#[:space:]].*:' Makefile

.PHONY: setup clean test debug publish build list lint black mypy
