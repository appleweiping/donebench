IMAGE ?= donebench-repro
RESULTS ?= results/smoke.jsonl
COST_INPUT ?= results/topconf_deepseek_core_trial0.jsonl

.PHONY: test validate audit quality readiness smoke figures paper repro-smoke repro-package repro-manifest openreview-package cost-report topconf-pilot topconf-full topconf-token-matched topconf-postprocess docker-build docker-smoke

test:
	pytest

validate:
	donebench validate data/tasks

audit:
	donebench audit-tasks data/tasks

quality:
	donebench quality-audit data/tasks reports/quality

readiness:
	donebench readiness-report data/tasks reports/readiness_report.json

smoke:
	donebench validate data/tasks
	donebench run-matrix --suite smoke --output results/smoke.jsonl
	donebench aggregate results/
	donebench make-figures results/ paper/figures/

full-api:
	donebench run-matrix --suite full_api --output results/full_api.jsonl
	donebench aggregate results/
	donebench make-figures results/ paper/figures/

repro-smoke: smoke repro-manifest openreview-package

repro-package: validate audit quality readiness repro-manifest openreview-package

repro-manifest:
	donebench repro-manifest reports/repro_manifest.json --results $(RESULTS)

openreview-package:
	donebench export-paper-package

cost-report:
	donebench cost-report $(COST_INPUT) reports/costs

topconf-pilot:
	donebench experiment-pipeline topconf_deepseek_toolplan_pilot --limit 50 --resume --max-workers 0

topconf-full:
	donebench experiment-pipeline topconf_deepseek_toolplan_full --resume --max-workers 0

topconf-token-matched:
	donebench experiment-pipeline topconf_deepseek_token_matched --resume --max-workers 0

topconf-postprocess:
	donebench experiment-pipeline topconf_deepseek_toolplan_pilot --postprocess-only

docker-build:
	docker build -t $(IMAGE) .

docker-smoke: docker-build
	docker run --rm $(IMAGE) make repro-smoke

figures:
	donebench make-figures results/ paper/figures/

paper:
	cd paper && pdflatex -interaction=nonstopmode main.tex || true
