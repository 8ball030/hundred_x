.PHONY: tests
tests:
	poetry run pytest tests -vv

fmt:
	poetry run black tests hundred_x examples
	poetry run isort tests hundred_x examples

lint:
	poetry run flake8 tests hundred_x examples

all: fmt lint tests

test-docs:
	echo making docs

release:
	$(eval current_version := $(shell poetry run tbump current-version))
	@echo "Current version is $(current_version)"
	$(eval new_version := $(shell python3 -c "import semver; print(semver.bump_patch('$(current_version)'))"))
	@echo "New version is $(new_version)"
	poetry run tbump $(new_version)

