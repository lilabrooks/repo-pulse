VENV := .venv
PY := $(VENV)/bin/python

.PHONY: test run venv

venv: $(PY)

$(PY): requirements.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r requirements.txt
	@touch $(PY)

test: venv
	$(PY) -m pytest -q

run: venv
	set -a; [ -f .env ] && . ./.env; set +a; \
	$(VENV)/bin/uvicorn app.main:app --port 8000
