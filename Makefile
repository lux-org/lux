init:
	pip install -r requirements.txt
test:
	black --check .
	python -m pytest tests/
test_all:
	black --check .
	python -m pytest tests/
	python -m pytest tests_sql/
.PHONY: init test