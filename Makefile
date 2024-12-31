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
RENDERCV := $(shell command -v rendercv 2> /dev/null)
JEKYLL := $(shell command -v jekyll 2> /dev/null || echo -e "\033[31mnot installed\033[0m")
BUNDLE := $(shell command -v bundle 2> /dev/null)
LATEX := $(shell command -v pdflatex 2> /dev/null)
BIBER := $(shell command -v biber 2> /dev/null)
POPPLER := $(shell command -v pdfunite 2> /dev/null)

# Variables
GITHUB_REPO ?= $(shell url=$$($(GIT) config --get remote.origin.url); echo $${url%.git})
GITHUB_USER_NAME ?= $(shell echo $(GITHUB_REPO) | $(AWK) -F/ 'NF>=4{print $$4}')
PYTHON_VERSION ?= 3.13.1
PYENV_VIRTUALENV_NAME ?= $(shell cat .python-version)

# Stamp files
STAMP_FILES := $(wildcard .*.stamp)

# Dirs
SRC := src
DOCS := docs
DOCS_SITE := docs/_site
RENDERCV_DIR := rendercv_output
APP_LETTER_DIR := application_letters
CERT_DIR := Certificates
CACHE_DIRS := $(wildcard .*_cache)

# Files
CV_FILE := Fabio_Calefato_CV
PUB_FILE := Fabio_Calefato_Publications
APP_LETTER_SRC := HPI
APP_LETTER_FILE := Fabio_Calefato_Application
PHD_CERT_FILE := $(CERT_DIR)/phd_certificate-ita.pdf
MSC_CERT_FILE := $(CERT_DIR)/msc_certificate-ita.pdf
PY_FILES := $(shell find . -type f -name '*.py')
DOCS_FILES := $(shell find $(DOCS) -type f -name '*.md') README.md
LATEX_TEMP_FILES := $(PUB_FILE).aux $(PUB_FILE).bbl $(PUB_FILE).blg $(PUB_FILE).log $(PUB_FILE).run.xml $(PUB_FILE).bcf 

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
	@echo -e "  $(CYAN)RenderCV:$(RESET) $(shell $(RENDERCV) --version || echo "$(RED)not installed $(RESET)")"
	@echo -e "  $(CYAN)LaTeX:$(RESET) $(shell $(LATEX) --version | head -n 1 || echo "$(RED)not installed $(RESET)")"
	@echo -e "  $(CYAN)biber:$(RESET) $(shell $(BIBER) --version || echo "$(RED)not installed $(RESET)")"
	@echo -e "  $(CYAN)poppler:$(RESET) $(shell $(POPPLER) --version | head -n 1 || echo "$(RED)not installed $(RESET)")"
	@echo -e "  $(CYAN)Jekyll:$(RESET) $(JEKYLL)"
	@echo -e "  $(CYAN)Bundler:$(RESET) $(shell $(BUNDLE) --version || echo "$(RED)not installed $(RESET)")"
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

#-- System

.PHONY: python
python: | dep/pyenv dep/git  ## Check if Python is installed
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
project/install: virtualenv requirements.txt  ## Install the project
	@if [ ! -f .python-version ]; then \
		echo -e "$(RED)\nVirtual environment missing. Please run 'make virtualenv' first.$(RESET)"; \
	else \
		echo -e "$(CYAN)\nInstalling project dependencies...$(RESET)"; \
		$(PYTHON) -m pip --upgrade pip; \
		$(PYTHON) -m pip -r requirements.txt; \
		echo -e "$(GREEN)Dependencies installed.$(RESET)"; \
	fi

.PHONY: project/update
project/update: virtualenv requirements.txt  ## Update the project
	@echo -e "$(CYAN)\nUpdating the project...$(RESET)"
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt --upgrade
	@echo -e "$(GREEN)Project updated.$(RESET)"

.PHONY: project/clean
project/clean:  ## Clean untracked output files
	@echo -e "$(YELLOW)\nCleaning...$(RESET)"
	@rm -rf $(STAMP_FILES) $(LATEX_TEMP_FILES) || true
	@rm -rf `$(BIBER) --cache` || true
	@echo -e "$(GREEN)Directory cleaned.$(RESET)"

project/import_biblio: python  ## Import bibliography
	@echo -e "$(CYAN)\nImporting bibliography...$(RESET)"
	@$(PYTHON) $(SRC)/parsebib.py
	@echo -e "$(GREEN)Bibliography imported.$(RESET)"

project/update_cv: python  ## Update CV input file with selected bibliography
	@echo -e "$(CYAN)\nUpdating CV input file with selected bibliography...$(RESET)" 
	@$(PYTHON) $(SRC)/pubmerger.py
	@echo -e "$(GREEN)CV input file updated.$(RESET)"

project/build_cv: | project/update_cv  ## Build pdf file of CV
	@echo -e "$(CYAN)\nBuild CV...$(RESET)" 
	@$(RENDERCV) render src/${CV_FILE}.yaml --pdf-path ${CV_FILE}.pdf --markdown-path README.md --latex-path ${CV_FILE}.tex --html-path ${CV_FILE}.html --dont-generate-png --use-local-latex-command pdflatex
	@$(PYTHON) $(SRC)/genmd.py
	@echo -e "$(GREEN)CV built.$(RESET)"

project/build_pubs: | project/import_biblio  ## Build pdf files of CV and publications
	@echo -e "$(CYAN)\nBuilding Publications...$(RESET)"
	@$(LATEX) $(PUB_FILE)
	@$(BIBER) $(PUB_FILE)
	@$(LATEX) $(PUB_FILE)
	@$(LATEX) $(PUB_FILE)
	@echo -e "$(GREEN)Publications built.$(RESET)"

project/build_application:  ## Build application letter
	@echo -e "$(CYAN)\nBuilding application letter...$(RESET)"
	cd $(APP_LETTER_DIR) && \
	$(LATEX) -output-directory=. -job-name=$(APP_LETTER_SRC) $(APP_LETTER_SRC).tex && \
	$(POPPLER) $(APP_LETTER_SRC).pdf ../$(CV_FILE).pdf ../$(PUB_FILE).pdf $(PHD_CERT_FILE) $(MSC_CERT_FILE) $(APP_LETTER_FILE)_$(APP_LETTER_SRC).pdf && \
	cd .. && \
	echo -e "$(GREEN)Application letter built.$(RESET)"

project/build_all: project/build_cv project/build_pubs project/build_application  ## Build all files
	@echo -e "$(GREEN)All files built.$(RESET)"

#-- Check

.PHONY: check/format
check/format:  ## Format the code
	@echo -e "$(CYAN)\nFormatting...$(RESET)"
	@ruff format $(PY_FILES)
	@echo -e "$(GREEN)Code formatted.$(RESET)"

.PHONY: check/lint
check/lint:  ## Lint the code
	@echo -e "$(CYAN)\nLinting...$(RESET)"
	@ruff check $(PY_FILES)
	@echo -e "$(GREEN)Code linted.$(RESET)"

#-- Release

.PHONY: release/version
release/version:  ## Tag and push to origin (use release/version ARGS="x.x.x")
	@$(eval TAG := $(ARGS))
	@$(eval REMOTE_TAGS := $(shell $(GIT) ls-remote --tags origin | $(AWK) '{print $$2}'))
	@if echo $(REMOTE_TAGS) | grep -q $(TAG); then \
		echo -e "$(YELLOW)\nNothing to push: tag $(TAG) already exists on origin.$(RESET)"; \
	else \
		echo -e "$(CYAN)\nCreating new version $(TAG)...$(RESET)"; \
		$(GIT) tag $(TAG); \
		echo -e "$(CYAN)\nPushing version $(TAG)...$(RESET)"; \
		$(GIT) push origin; \
		$(GIT) push origin $(TAG); \
		echo -e "$(GREEN)Release $(TAG) pushed.$(RESET)"; \
	fi

#-- Pages

pages/serve:  ## Serve the GitHub Pages html file locally
	@echo -e "$(CYAN)\nServing the documentation...$(RESET)"
	@echo -e "$(YELLOW)Press Ctrl+C to stop the server.$(RESET)"
	@$(BUNDLE) exec jekyll serve --source $(DOCS) --destination $(DOCS_SITE)
	@echo -e "$(GREEN)Documentation served.$(RESET)"