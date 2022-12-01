.PHONY: tests

tests:
	pytest

install-dev:
	pip install --upgrade pip wheel setuptools
	poetry install

style-python:
	isort .
	flake8

check-style-python-ci:
	isort . -c
	flake8
