PYTHON=python -m

POETRY=poetry
POETRY_RUN=$(POETRY) run

COVERAGE=coverage
COVERAGE_RUN=$(COVERAGE) run -m

UVICORN=uvicorn
ENTRYPOINT=src.main
APP=app

DVC=dvc
DVC_GET=$(DVC) get -f
DATA_REPO_URL=https://dagshub.com/diego-garro/metar-forecast

SOURCE_FILES=$(shell find . -path "./src/*.py")
TEST_FILES=$(shell find . -path "./tests/**/*.py")
SOURCES_FOLDER=src

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

check_no_main:
ifeq ($(BRANCH),main)
	echo "You are good to go!"
else
	$(error You are not in the main branch)
endif

check:
	mypy --config-file mypy.ini aeromet_py/

patch: check_no_main
	$(POETRY_RUN) bumpversion patch --verbose
	git push --follow-tags

minor: check_no_main
	$(POETRY_RUN) bumpversion minor --verbose
	git push --follow-tags

major: check_no_main
	$(POETRY_RUN) bumpversion major --verbose
	git push --follow-tags

style:
	$(POETRY_RUN) isort $(SOURCES_FOLDER)
	$(POETRY_RUN) black $(SOURCE_FILES)

lint:
	$(POETRY_RUN) isort $(SOURCES_FOLDER) --check-only
	$(POETRY_RUN) black $(SOURCE_FILES) --check

test:
	$(POETRY_RUN) pytest tests

test-verbose:
	$(POETRY_RUN) pytest tests -vv

coverage:
	$(POETRY_RUN) $(COVERAGE_RUN) pytest tests
	$(POETRY_RUN) $(COVERAGE) html --skip-covered --skip-empty

codecov:
	$(POETRY_RUN) codecov

run:
	$(POETRY_RUN) $(PYTHON) $(SOURCES_FOLDER)

dvc-download:
    $(DVC_GET) $(DATA_REPO_URL) data