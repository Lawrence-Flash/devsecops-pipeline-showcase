IMAGE ?= tickets-api:local
CLUSTER_DIR := infra/terraform/cluster
PLATFORM_DIR := infra/terraform/platform

.PHONY: test lint image policy scan sbom up down

test:
	python -m pytest

lint:
	ruff check .
	ruff format --check .

image:
	docker build -t $(IMAGE) .

policy:
	bash scripts/policy_check.sh

scan: image
	trivy fs --skip-dirs policies/testdata --severity HIGH,CRITICAL --exit-code 1 --scanners vuln,misconfig,secret .
	trivy image --severity HIGH,CRITICAL --exit-code 1 --scanners vuln,secret $(IMAGE)

sbom: image
	trivy image --format cyclonedx --output sbom.cdx.json $(IMAGE)

up: image
	terraform -chdir=$(CLUSTER_DIR) init -input=false
	terraform -chdir=$(CLUSTER_DIR) apply -auto-approve -var app_image=$(IMAGE)
	terraform -chdir=$(PLATFORM_DIR) init -input=false
	terraform -chdir=$(PLATFORM_DIR) apply -auto-approve

down:
	-terraform -chdir=$(PLATFORM_DIR) destroy -auto-approve
	terraform -chdir=$(CLUSTER_DIR) destroy -auto-approve
