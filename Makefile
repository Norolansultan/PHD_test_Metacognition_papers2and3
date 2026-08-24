.PHONY: setup test run replay terrain viewer api e2e demo clean

PY ?= python3
SCENARIO ?= scenarios/fin-def-03.yaml

setup:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m pytest tests/ -q

terrain:
	$(PY) tools/make_terrain.py

run:
	$(PY) -m harness.run --scenario $(SCENARIO) \
	  --participant harness/participants/synth_01.yaml --out logs/synth_01.jsonl
	$(PY) -m harness.run --scenario $(SCENARIO) \
	  --participant harness/participants/synth_02_no_ask.yaml --out logs/synth_02.jsonl

replay:
	$(PY) -m harness.replay logs/synth_01.jsonl logs/replay_01.jsonl

viewer: run
	$(PY) tools/make_viewer.py logs/viewer-data.json

api:
	$(PY) -m uvicorn api.main:app --port 8000 --reload

# End to end: a real browser against a real server. Start the API first.
e2e:
	$(PY) tools/e2e_check.py

# Everything from a clean checkout, in the order the build order specifies.
demo: setup terrain test run viewer
	@echo "engine ok, scenario ran, logs in logs/"
