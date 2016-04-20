.PHONY: clean release test

clean:
	find . -name "*.pyc" | xargs rm

release:
	tools/release_new_version.sh

test:
	python2.7 src/test_npm.py
	python2.7 src/test_semver.py
	python2.7 src/test_manifest.py
