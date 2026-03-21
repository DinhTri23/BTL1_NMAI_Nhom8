PROJECT_DIR := kakurasu/Kakurasu-Game-With-AI-Solver-Using-Search-Algorithm
VENV ?= .venv
REQ_FILE := $(PROJECT_DIR)/requirements.txt

ifeq ($(OS),Windows_NT)
PYTHON ?= py
VENV_PYTHON := $(VENV)/Scripts/python.exe
ACTIVATE_HINT := .\\$(VENV)\\Scripts\\Activate.ps1
else
PYTHON ?= python3
VENV_PYTHON := $(VENV)/bin/python
ACTIVATE_HINT := source $(VENV)/bin/activate
endif

.PHONY: help venv install activate deactivate run clean

help:
	@echo Available targets:
	@echo   make venv       - Create virtual environment and upgrade pip
	@echo   make install    - Install project dependencies into venv
	@echo   make activate   - Print the command to activate venv
	@echo   make deactivate - Reminder command to deactivate venv
	@echo   make run        - Run the Kakurasu game using venv Python
	@echo   make clean      - Remove the virtual environment

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV_PYTHON)
	"$(VENV_PYTHON)" -m pip install --upgrade pip

install: venv
	"$(VENV_PYTHON)" -m pip install -r "$(REQ_FILE)"

activate: venv
	@echo Run this command in your shell to activate the virtual environment:
	@echo $(ACTIVATE_HINT)

deactivate:
	@echo If your virtual environment is active, run: deactivate

run: install
	cd "$(PROJECT_DIR)" && "$(abspath $(VENV_PYTHON))" main.py

clean:
ifeq ($(OS),Windows_NT)
	powershell -NoProfile -Command "if (Test-Path '$(VENV)') { Remove-Item -Recurse -Force '$(VENV)' }"
else
	rm -rf "$(VENV)"
endif
