VENV := .venv
PYTHON := $(VENV)/Scripts/python.exe
PIP := $(VENV)/Scripts/pip.exe
PYINSTALLER := $(VENV)/Scripts/pyinstaller.exe
SPEC := PadelTournament.spec

.PHONY: build env clean distclean

build: env $(SPEC)
	"$(PYINSTALLER)" "$(SPEC)"

env:
	@if not exist "$(VENV)" (
		python -m venv "$(VENV)"
	)
	"$(PYTHON)" -m pip install -U pip
	"$(PIP)" install -e .
	"$(PIP)" install pyinstaller

clean:
	@if exist build rmdir /S /Q build
	@if exist dist rmdir /S /Q dist

