#!/bin/sh
# Idempotently seeds the Traefik discovery tags that every NotebookUM
# microservice reads back from Consul KV when it registers itself
# (see */app/consul_registration.py and controller-service/internal/config/consul.go).
#
# Without these keys, services register in Consul with an empty Tags list,
# and Traefik's consulCatalog provider (exposedByDefault: false) ignores them.
#
# Each KV leaf under config/<service>/traefik/** maps 1:1 to a Traefik tag:
# "/" becomes "." and the whole path is prefixed with "traefik.".
set -eu

put() {
  echo "  kv put $1"
  consul kv put "$1" "$2" >/dev/null
}

seed_service() {
  service="$1"
  host_rule="$2"
  middlewares="$3"
  port="$4"

  echo "Seeding Traefik tags for: $service"
  put "config/${service}/traefik/enable" "true"
  put "config/${service}/traefik/http/routers/${service}/rule" "$host_rule"
  put "config/${service}/traefik/http/routers/${service}/entrypoints" "http,https"
  put "config/${service}/traefik/http/routers/${service}/middlewares" "$middlewares"
  put "config/${service}/traefik/http/services/${service}/loadbalancer/server/port" "$port"
}

seed_service "controller-service" 'Host(`api.universidad.localhost`)' "rate-limit@file,circuit-breaker@file,request-tracing@file,cors-headers@file" "5000"
seed_service "user-service"       'Host(`users.universidad.localhost`)' "rate-limit@file,cors-headers@file" "5000"
seed_service "extract-service"    'Host(`extractor.universidad.localhost`)' "rate-limit@file,cors-headers@file" "5000"
seed_service "summary-service"    'Host(`ai.universidad.localhost`)' "rate-limit@file,cors-headers@file" "5000"

echo "✓ Consul KV seed complete"
