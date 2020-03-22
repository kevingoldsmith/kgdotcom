test:
	scripts/run_tests.sh

debug:
	scripts/build.sh -cd

clean:
	scripts/build.sh -c

publish:
	scripts/publish.sh
