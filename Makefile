# Shell config
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Make config
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Executables
MAKE_VERSION := $(shell make --version | head -n 1 2> /dev/null)
SED := $(shell command -v sed 2> /dev/null)
SED_INPLACE := $(shell if $(SED) --version >/dev/null 2>&1; then echo "$(SED) -i"; else echo "$(SED) -i ''"; fi)
AWK := $(shell command -v awk 2> /dev/null)
GREP := $(shell command -v grep 2> /dev/null)
PYENV := $(shell command -v pyenv 2> /dev/null)
PYTHON := $(shell command -v python 2> /dev/null)
PYENV_ROOT := $(shell pyenv root)
GIT := $(shell command -v git 2> /dev/null)
GIT_VERSION := $(shell $(GIT) --version 2> /dev/null || echo -e "\033[31mnot installed\033[0m")

# Variables
GITHUB_REPO ?= $(shell url=$$($(GIT) config --get remote.origin.url); echo $${url%.git})
GITHUB_USER_NAME ?= $(shell echo $(GITHUB_REPO) | $(AWK) -F/ 'NF>=4{print $$4}')
PYTHON_VERSION ?= 3.13.1
PYENV_VIRTUALENV_NAME ?= $(shell cat .python-version)

# Stamp files
INSTALL_STAMP := .install.stamp
DEPS_EXPORT_STAMP := .deps-export.stamp
BUILD_STAMP := .build.stamp
DOCS_STAMP := .docs.stamp
RELEASE_STAMP := .release.stamp
STAGING_STAMP := .staging.stamp
STAMP_FILES := $(wildcard .*.stamp)

# Dirs
SRC := src
DOCS := docs
DOCS_SITE := docs/_site
CACHE_DIRS := $(wildcard .*_cache)

# Files
CV_FILE := Fabio_Calefato_CV.yaml
PUB_FILE := Fabio_Calefato_Publications
PY_FILES := $(shell find . -type f -name '*.py')
DOCS_FILES := $(shell find $(DOCS) -type f -name '*.md') README.md
PROJECT_INIT := .project-init

# Colors
RESET := \033[0m
RED := \033[1;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
MAGENTA := \033[1;35m
CYAN := \033[0;36m

# Intentionally left empty
ARGS ?=

#-- Info

.DEFAULT_GOAL := help
.PHONY: help
help:  ## Show this help message
	@echo -e "\n$(MAGENTA)Usage:\n$(RESET)  make $(CYAN)[target] [ARGS=\"...\"]$(RESET)\n"
	@grep -E '^[0-9a-zA-Z_-]+(/?[0-9a-zA-Z_-]*)*:.*?## .*$$|(^#--)' $(firstword $(MAKEFILE_LIST)) \
	| $(AWK) 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-21s\033[0m %s\n", $$1, $$2}' \
	| $(SED) -e 's/\[36m  #-- /\[1;35m/'

.PHONY: info
info:  ## Show development environment info
	@echo -e "$(MAGENTA)\nSystem:$(RESET)"
	@echo -e "  $(CYAN)OS:$(RESET) $(shell uname -s)"
	@echo -e "  $(CYAN)Shell:$(RESET) $(SHELL) - $(shell $(SHELL) --version | head -n 1)"
	@echo -e "  $(CYAN)Make:$(RESET) $(MAKE_VERSION)"
	@echo -e "  $(CYAN)Git:$(RESET) $(GIT_VERSION)"
	@echo -e "$(MAGENTA)Project:$(RESET)"
	@echo -e "  $(CYAN)Project repository:$(RESET) $(GITHUB_REPO)"
	@echo -e "  $(CYAN)Project directory:$(RESET) $(CURDIR)"
	@echo -e "$(MAGENTA)Python:$(RESET)"
	@echo -e "  $(CYAN)Python version:$(RESET) $(PYTHON_VERSION)"
	@echo -e "  $(CYAN)Pyenv version:$(RESET) $(shell $(PYENV) --version || echo "$(RED)not installed $(RESET)")"
	@echo -e "  $(CYAN)Pyenv root:$(RESET) $(PYENV_ROOT)"
	@echo -e "  $(CYAN)Pyenv virtualenv name:$(RESET) $(PYENV_VIRTUALENV_NAME)"
	
# Dependencies

.PHONY: dep/git
dep/git:
	@if [ -z "$(GIT)" ]; then echo -e "$(RED)Git not found.$(RESET)" && exit 1; fi

.PHONY: dep/pyenv
dep/pyenv:
	@if [ -z "$(PYENV)" ]; then echo -e "$(RED)Pyenv not found.$(RESET)" && exit 1; fi

.PHONY: dep/python
dep/python: dep/pyenv
	@if [ -z "$(PYTHON)" ]; then echo -e "$(RED)Python not found.$(RESET)" && exit 1; fi

#-- System

.PHONY: python
python: | dep/pyenv  ## Check if Python is installed
	@if ! $(PYENV) versions | grep $(PYTHON_VERSION) > /dev/null ; then \
		echo -e "$(RED)Python version $(PYTHON_VERSION) not installed.$(RESET)"; \
		echo -e "$(RED)To install it, run '$(PYENV) install $(PYTHON_VERSION)'.$(RESET)"; \
		echo -e "$(RED)Then, re-run 'make virtualenv'.$(RESET)"; \
		exit 1 ; \
	else \
		echo -e "$(CYAN)\nPython version $(PYTHON_VERSION) available.$(RESET)"; \
	fi

.PHONY: virtualenv
virtualenv: | python  ## Check if virtualenv exists and activate it - create it if not
	@if ! $(PYENV) virtualenvs | grep $(PYENV_VIRTUALENV_NAME) > /dev/null ; then \
		echo -e "$(YELLOW)\nLocal virtualenv not found. Creating it...$(RESET)"; \
		$(PYENV) virtualenv $(PYTHON_VERSION) $(PYENV_VIRTUALENV_NAME) || exit 1; \
		echo -e "$(GREEN)Virtualenv created.$(RESET)"; \
	else \
		echo -e "$(CYAN)\nVirtualenv already created.$(RESET)"; \
	fi
	@$(PYENV) local $(PYENV_VIRTUALENV_NAME)
	@echo -e "$(GREEN)Virtualenv activated.$(RESET)"


#-- Project

.PHONY: project/install
project/install: virtualenv $(INSTALL_STAMP)  ## Install the project for development
$(INSTALL_STAMP): requirements.txt
	@if [ ! -f .python-version ]; then \
		echo -e "$(RED)\nVirtual environment missing. Please run 'make virtualenv' first.$(RESET)"; \
	else \
		echo -e "$(CYAN)\nInstalling project dependencies...$(RESET)"; \
		@$(PYTHON) -m pip --upgrade pip; \
		@$(PYTHON) -m pip -r requirements.txt; \
		echo -e "$(GREEN)Dependencies installed.$(RESET)"; \
		touch $(INSTALL_STAMP); \
	fi

.PHONY: project/update
project/update: | project/install  ## Update the project
	@echo -e "$(CYAN)\nUpdating the project...$(RESET)"
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt --upgrade
	@echo -e "$(GREEN)Project updated.$(RESET)"

.PHONY: project/clean
project/clean:  ## Clean the project - removes all cache dirs and stamp files
	@echo -e "$(YELLOW)\nCleaning the project...$(RESET)"
	@find . -type d -name "__pycache__" | xargs rm -rf {};
	@rm -rf $(STAMP_FILES) $(CACHE_DIRS) $(DOCS_SITE) || true
	@echo -e "$(GREEN)Project cleaned.$(RESET)"


project/import_biblio: dep/python $(INSTALL_STAMP)  ## Import bibliography
	@echo -e "$(CYAN)\nImporting bibliography...$(RESET)"
	@$(PYTHON) $(SRC)/parsebib.py
	@echo -e "$(GREEN)Bibliography imported.$(RESET)"

project/update_cv: dep/python $(INSTALL_STAMP) ## Update CV input file with selected bibliography
	@echo -e "$(CYAN)\nUpdating CV input file with selected bibliography...$(RESET)" 
	@$(PYTHON) $(SRC)/pubmerger.py
	@echo -e "$(GREEN)CV input file updated.$(RESET)"

project/build_cv: | project/update_cv  ## Build pdf file of CV
	@echo -e "$(CYAN)\nBuild CV...$(RESET)" 
	rendercv render src/${CV_FILE} --pdf-path ${CV_FILE}.yaml.pdf --markdown-path README.md --latex-path ${CV_FILE}.yaml.tex --html-path ${CV_FILE}.yaml.html --dont-generate-png --use-local-latex-command pdflatex
	@echo -e "$(GREEN)CV built.$(RESET)"

project/build_pubs: | project/import_biblio  ## Build pdf files of CV and publications
	@echo -e "$(CYAN)\nBuilding Publications...$(RESET)"
	@pdflatex $(PUB_FILE)
	@biber $(PUB_FILE)
	@pdflatex $(PUB_FILE)
	@pdflatex $(PUB_FILE)
	@echo -e "$(GREEN)Publications built.$(RESET)"

project/buildall: project/build_cv project/build_pubs
	@echo -e "$(GREEN)All files built.$(RESET)"

#-- Check

.PHONY: check/format
check/format: $(INSTALL_STAMP)  ## Format the code
	@echo -e "$(CYAN)\nFormatting the code...$(RESET)"
	@ruff format $(PY_FILES)
	@echo -e "$(GREEN)Code formatted.$(RESET)"

.PHONY: check/lint
check/lint: $(INSTALL_STAMP)  ## Lint the code
	@echo -e "$(CYAN)\nLinting the code...$(RESET)"
	@ruff check $(PY_FILES)
	@echo -e "$(GREEN)Code linted.$(RESET)"

#-- Release

.PHONY: tag
tag: | dep/git
	@$(eval TAG := $(shell $(GIT) describe --tags --abbrev=0))
	@$(eval BEHIND_AHEAD := $(shell $(GIT) rev-list --left-right --count $(TAG)...origin/main))
	@$(shell if [ "$(BEHIND_AHEAD)" = "0	0" ]; then echo "false" > $(RELEASE_STAMP); else echo "true" > $(RELEASE_STAMP); fi)
	@echo -e "$(CYAN)\nChecking if a new release is needed...$(RESET)"
	@echo -e "  $(CYAN)Current tag:$(RESET) $(TAG)"
	@echo -e "  $(CYAN)Commits behind/ahead:$(RESET) $(shell echo ${BEHIND_AHEAD} | tr '[:space:]' '/' | $(SED) 's/\/$$//')"
	@echo -e "  $(CYAN)Needs release:$(RESET) $(shell cat $(RELEASE_STAMP))"

.PHONY: staging
staging: | dep/git
	@if $(GIT) diff --cached --quiet; then \
		echo "true" > $(STAGING_STAMP); \
	else \
		echo "false" > $(STAGING_STAMP); \
	fi; \
	echo -e "$(CYAN)\nChecking the staging area...$(RESET)"; \
	echo -e "  $(CYAN)Staging area empty:$(RESET) $$(cat $(STAGING_STAMP))"

.PHONY: release/version
release/version: | tag staging  ## Tag a new release version
	@NEEDS_RELEASE=$$(cat $(RELEASE_STAMP)); \
	if [ "$$NEEDS_RELEASE" = "true" ]; then \
		case "$(ARGS)" in \
			"patch"|"minor"|"major"|"prepatch"|"preminor"|"premajor"|"prerelease"|"--next-phase") \
				echo -e "$(CYAN)\nCreating a new version...$(RESET)"; \
				;; \
			*) \
				echo -e "$(RED)Invalid version argument.$(RESET)"; \
				echo -e "$(RED)\nUsage: make release/version ARGS=\"patch|minor|major|prepatch|preminor|premajor|prerelease|--next-phase\"$(RESET)"; \
				exit 1; \
				;; \
		esac; \
		$(eval TAG := $(shell $(GIT) describe --tags --abbrev=0)) \
		$(eval NEW_TAG := $(shell $(POETRY) version $(ARGS) > /dev/null && $(POETRY) version -s)) \
		$(GIT) add pyproject.toml; \
		$(GIT) commit -m "Bump version to $(NEW_TAG)"; \
		echo -e "$(CYAN)\nTagging a new patch version... [$(TAG)->$(NEW_TAG)]$(RESET)"; \
		$(GIT) tag $(NEW_TAG); \
		echo -e "$(GREEN)New patch version tagged.$(RESET)"; \
	else \
		echo -e "$(YELLOW)\nNo new release needed.$(RESET)"; \
	fi

.PHONY: release/publish
release/publish: | dep/git  ## Push the tagged version to origin - triggers the release and docker actions
	@$(eval TAG := $(shell $(GIT) describe --tags --abbrev=0))
	@$(eval REMOTE_TAGS := $(shell $(GIT) ls-remote --tags origin | $(AWK) '{print $$2}'))
	@if echo $(REMOTE_TAGS) | grep -q $(TAG); then \
		echo -e "$(YELLOW)\nNothing to push: tag $(TAG) already exists on origin.$(RESET)"; \
	else \
		echo -e "$(CYAN)\nPushing new release $(TAG)...$(RESET)"; \
		$(GIT) push origin; \
		$(GIT) push origin $(TAG); \
		echo -e "$(GREEN)Release $(TAG) pushed.$(RESET)"; \
	fi