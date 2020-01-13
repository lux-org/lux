init:
    pip install -r requirements.txt
test:
    python -m pytest tests/
.PHONY: init test