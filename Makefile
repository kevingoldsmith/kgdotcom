venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/bin/activate

checkpoint: output
	rm -rf lkgoutput
	cp -r output lkgoutput

checkpoint-debug: testoutput
	rm -rf lkgtestoutput
	cp -r testoutput lkgtestoutput

clean:
	scripts/build.sh -c

test: venv/bin/activate
	. venv/bin/activate; scripts/run_tests.sh

debug: venv/bin/activate
	. venv/bin/activate; scripts/build.sh -cd

build: venv/bin/activate
	. venv/bin/activate; scripts/build.sh

publish: venv/bin/activate
	. venv/bin/activate; scripts/publish.sh

lint: venv/bin/activate
	. venv/bin/activate; pylint *.py

black: venv/bin/activate
	. venv/bin/activate; black .

mypy: venv/bin/activate
	. venv/bin/activate; mypy --disallow-untyped-defs .

scan: venv/bin/activate
	. venv/bin/activate; pip-audit > pip-audit-report.txt || true
	. venv/bin/activate; bandit -r . -f json -o security-report.json
	# safety scan - need to register

testcheckpoint: output
	python3 tests/compare_outputs.py output lkgoutput

testdebugcheckpoint: testoutput
	python3 tests/compare_outputs.py testoutput lkgtestoutput

list:
	@grep '^[^#[:space:]].*:' Makefile

.PHONY: clean test debug publish build list lint black mypy scan checkpoint checkpoint-debug
