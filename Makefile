init:
	pip install -r requirements.txt
test:
	black --check .
	python -m pytest tests/

.PHONY: init test