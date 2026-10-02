#!/usr/bin/env bash
# Render the chart and evaluate it with the same Kyverno policies the cluster will enforce.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rendered="$(mktemp)"
trap 'rm -f "$rendered"' EXIT

helm lint "$root/charts/tickets-api"
helm template tickets-api "$root/charts/tickets-api" --namespace tickets >"$rendered"
kyverno apply "$root/policies/kyverno" --resource "$rendered"
kyverno apply "$root/policies/kyverno" --resource "$root/policies/testdata/good-pod.yaml"

expect_reject() {
  local policy="$1"
  local resource="$2"
  local name="$3"
  local log
  log="$(mktemp)"
  set +e
  kyverno apply "$policy" --resource "$resource" >"$log" 2>&1
  local code=$?
  set -e
  if [[ "$code" -eq 0 ]]; then
    echo "expected ${name} to be rejected by Kyverno" >&2
    cat "$log" >&2
    rm -f "$log"
    exit 1
  fi
  rm -f "$log"
  echo "rejected ${name} as expected"
}

expect_reject \
  "$root/policies/kyverno/disallow-privileged.yaml" \
  "$root/policies/testdata/privileged-pod.yaml" \
  "privileged pod"
expect_reject \
  "$root/policies/kyverno/disallow-latest-tag.yaml" \
  "$root/policies/testdata/latest-tag-pod.yaml" \
  "latest tag"

echo "Kyverno policy check passed"
