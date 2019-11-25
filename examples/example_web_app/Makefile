#############################################
#                                           #
# MAKEFILE FOR DEFINING A MANAGEMENT CLI    #
#                                           #
#############################################

# Setup the shell and python version.
# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
PYTHON := python3

# Constants
VENV_DIR_LINK = venv
VENV_DIR = .example_web_app-venv
TEST_VENV_DIR = .testing-venv
SHELL_NAME = bash
RUN_DEV_SERVER = adev runserver -v example_web_app/app.py --app-factory create_app -p 8137

.PHONY: help clean clean-venv clean-temp-files venv install install-dev package dev-upgrade-deps test test-unit test-integration test-end-to-end pytest cover coverage lint flake8


#################################
#                               #
# HELP                      	#
#                               #
#################################
help:
	@echo "usage: make <command>"
	@echo
	@echo "The available commands are:"
	@echo "  clean              [alias] for running \"clean-venv\" and \"clean-temp-files\" sequentially."
	@echo "  clean-venv         to clean the virtualenv directories and links."
	@echo "  clean-temp-files   to cleanup the project from temporary files."
	@echo "  venv-app           to create the applications virtualenv and its symbolic links."
	@echo "  venv-test          to create the testing virtualenv for hosting dev requirements and running tests."
	@echo "  install            to install the app, runs \"venv\" automatically."
	@echo "  install-dev        to install the app in editable mode, runs \"venv\" automatically."
	@echo "  package            to create a package ready for deployment."
	@echo "  dev-upgrade-deps   [dev-tool] runs \"clean\", \"install\" and then uses pip to upgrade requirements using the floating file."
	@echo "  dev-server         [dev-tool] runs a development server with auto-reloading on source file changes."
	@echo "  tox                to run the tests package on several Python run-times with tox."
	@echo "  pytest             to run the entire tests package."
	@echo "  test               [alias] for running \"install-dev\" and \"pytest\" sequentially."
	@echo "  test-unit          to run the unit tests only (tests/unit_tests package)."
	@echo "  test-integration   to run the integration tests only (tests/integration_tests package)."
	@echo "  test-end-to-end    to run the end-to-end tests only (tests/end_to_end_tests package)."
	@echo "  flake8             to run flake8 linting on the project."
	@echo "  coverage           to generate unit tests coverage."
	@echo "  help               to display this message."
	@echo
	@echo "All testing commands take a \"VERBOSITY\" argument which is by default set to 'vv'. It controls the verbosity of the pytest command. For example: \`make unit-tests VERBOSITY=qq\`."


#################################
#                               #
# CLEAN-UP                  	#
#                               #
#################################
clean-venv:
	@echo "####################################################"
	@echo "# CLEANING UP THE VIRTUAL ENVIRONMENT              #"
	@echo "####################################################"
	@rm -rf $(VENV_DIR)
	@rm -rf $(VENV_DIR_LINK)
	@rm -rf $(TEST_VENV_DIR)
	@echo "Done!"


clean-temp-files:
	@echo "####################################################"
	@echo "# CLEANING UP CACHED AND TMP FILES                 #"
	@echo "####################################################"
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf .tox
	@rm -rf htmlcov
	@rm -rf .cache
	@rm -rf .pytest_cache
	@find . -name "*.*,cover" -delete
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "__pycache__" -exec rm -rf {} \; || echo "";
	@echo "Done!"


clean: clean-venv clean-temp-files


#################################
#                               #
# VIRTUAL ENVIRONMENT       	#
#                               #
#################################
log-py-version:
	@echo -n "[INFO] Make is using the Python version: "
	@$(PYTHON) -c 'import sys; v = sys.version_info; print(f"{v.major}.{v.minor}.{v.micro}-{v.releaselevel}");'


venv-app:
	@echo "####################################################"
	@echo "# CREATING THE VIRTUAL ENVIRONMENT                 #"
	@echo "####################################################"
	@echo "===================================================="
	@$(MAKE) -s log-py-version
	@echo "===================================================="
	@test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	@test -d $(VENV_DIR_LINK) || ln -s $(VENV_DIR) $(VENV_DIR_LINK)
	@echo "Done!"


venv-test:
	@echo "####################################################"
	@echo "# CREATING THE >>> TEST <<< VIRTUAL ENVIRONMENT    #"
	@echo "####################################################"
	@echo "===================================================="
	@$(MAKE) -s log-py-version
	@echo "===================================================="
	@test -d $(TEST_VENV_DIR) || $(PYTHON) -m venv $(TEST_VENV_DIR);
	@echo "Done!"


#################################
#                               #
# INSTALLATION                  #
#                               #
#################################
install: venv-app
	@echo "####################################################"
	@echo "# ACTIVATING VENV & RESOLVING DEPENDENCIES         #"
	@echo "####################################################"
	@. $(VENV_DIR)/bin/activate \
		&& pip install -U pip \
		&& pip install -U .
	@echo "Done!"


install-dev: venv-test
	@echo "####################################################"
	@echo "# CREATING TESTING VENV AND INSTALLING DEV DEPS    #"
	@echo "####################################################"
	@. $(TEST_VENV_DIR)/bin/activate \
		&& pip install -U pip \
		&& pip install -e . \
		&& pip install -U -r requirements_dev.txt
	@echo "Done!"


#################################
#                               #
# PACKAGING                     #
#                               #
#################################
package:
	@echo "####################################################"
	@echo "# CREATING A PACKAGE FOR DEPLOYMENT                #"
	@echo "####################################################"
	@command -v wheel >/dev/null 2>&1 || { pip install wheel; }
	@git submodule update --init
	@rm -rf dist
	@. $(VENV_DIR)/bin/activate \
		&& pip install -U setuptools wheel \
		&& $(PYTHON) setup.py bdist_wheel --dist-dir=dist
	@echo "Done!"


#################################
#                               #
# DEVELOPMENT TOOLS             #
#                               #
#################################
dev-upgrade-deps: clean install
	@echo "####################################################"
	@echo "# UPGRADING DEPENDENCIES                           #"
	@echo "####################################################"
	@. $(VENV_DIR)/bin/activate \
		&& pip install -U -r requirements_floating.txt \
		&& pip freeze | egrep -v example_web_app > requirements.txt
	@echo "===================================================="
	@git diff requirements.txt
	@echo "===================================================="
	@echo "Done!"


dev-server:
	@echo "####################################################"
	@echo "# STARTING THE >>> DEVELOPMENT <<< SERVER          #"
	@echo "####################################################"
	@test -d $(TEST_VENV_DIR) && test -s $(TEST_VENV_DIR)/bin/adev || { \
		echo "Please run 'make install-dev' first!"; \
		exit 1; \
	}
	@. $(TEST_VENV_DIR)/bin/activate && $(RUN_DEV_SERVER)


#################################
#                               #
# TESTS AND COVERAGE            #
#                               #
#################################
VERBOSITY=vq
PYTEST_ARGS=
pytest:
	@echo "####################################################"
	@echo "# [TESTING] RUNNING ALL TESTS                      #"
	@echo "####################################################"
	@test -d $(TEST_VENV_DIR) || { echo "Please run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && py.test --cache-clear -$(VERBOSITY) $(PYTEST_ARGS)


VERBOSITY=vq
test: install-dev
	@$(MAKE) -s pytest VERBOSITY=$(VERBOSITY)


VERBOSITY=vq
cover coverage:
	@echo "####################################################"
	@echo "# [TESTING] ANALYSING TEST COVERAGE                #"
	@echo "####################################################"
	@test -d $(TEST_VENV_DIR) || { echo "Please run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate \
		&& coverage run --source example_web_app/ `which py.test` --cache-clear -$(VERBOSITY) tests/unit_tests; \
		coverage report; \
		coverage html;
	@echo "coverage report done! To see it run something like 'chromium-browser htmlcov/index.html'"


lint flake8:
	@echo "####################################################"
	@echo "# [TESTING] LINTING CODE WITH FLAK8                #"
	@echo "####################################################"
	@test -d $(TEST_VENV_DIR) || { echo "Please run 'make install-dev' first!"; exit 1; }
	@. $(TEST_VENV_DIR)/bin/activate && flake8 ty/


#################################
#                               #
# DOCKERIZATION                 #
#                               #
#################################
docker-build:
	@docker build -t example_web_app:latest .

docker-run:
	@docker run --rm -it -p 9999:9999 example_web_app

docker-build-run: docker-build docker-run
