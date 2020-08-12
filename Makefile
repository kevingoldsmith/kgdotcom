setup:
	python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/bin/activate

test: venv
	. venv/bin/activate; nosetests project/test

clean:
	rm -rf venv
	find -iname "*.pyc" -delete
	scripts/build.sh -c

test:
	scripts/run_tests.sh

debug:
	scripts/build.sh -cd

publish:
	scripts/publish.sh

.PHONY: setup clean test debug publish
