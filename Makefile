POETRY=poetry
POETRY_RUN=$(POETRY) run

SOURCE_FILES=$(shell find . -path "./metar_forecast/*.py")
SOURCES_FOLDER=metar_forecast

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

check_no_main:
ifeq ($(BRANCH),main)
	echo "You are good to go!"
else
	$(error You are not in the main branch)
endif

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