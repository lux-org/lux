init:
	pip install -r requirements.txt
test:
	black --check .
	python -m pytest tests/
test-pandas:
	python -m pytest tests_pandas/*.py
	python -m pytest tests_pandas/*/*.py

.PHONY: init test