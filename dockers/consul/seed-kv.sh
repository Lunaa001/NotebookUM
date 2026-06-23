#!/bin/bash
# ============================================================================
# NotebookUM — Seed Consul KV Store
# Carga toda la configuración de los microservicios en Consul KV.
# Ejecutar UNA VEZ después de levantar Consul.
#
# Uso: bash seed-kv.sh [CONSUL_ADDR]
#   CONSUL_ADDR default: http://localhost:8500
# ============================================================================

set -euo pipefail

CONSUL_ADDR="${1:-http://localhost:8500}"
CONSUL_TOKEN="2be22662-4819-4a0c-81d9-b3f50c4c389c"

put_kv() {
  local key="$1"
  local value="$2"
  curl -s -X PUT \
    -H "X-Consul-Token: ${CONSUL_TOKEN}" \
    -d "${value}" \
    "${CONSUL_ADDR}/v1/kv/${key}" > /dev/null
  echo "  ✓ ${key}"
}

echo "═══════════════════════════════════════════════════════════"
echo "  NotebookUM — Cargando configuración en Consul KV"
echo "  Consul: ${CONSUL_ADDR}"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─── Controller Service (Go) ─────────────────────────────────────────────
echo "▸ controller-service"
put_kv "config/controller-service/PORT"                  "5000"
put_kv "config/controller-service/X_CORRELATION_HEADER"  "X-Correlation-ID"
put_kv "config/controller-service/X_USER_ID_HEADER"      "X-User-ID"
put_kv "config/controller-service/USER_SERVICE_URL"      "http://users.universidad.localhost:5000"
put_kv "config/controller-service/EXTRACT_SERVICE_URL"   "http://extractor.universidad.localhost:5000"
put_kv "config/controller-service/SUMMARY_SERVICE_URL"   "http://ai.universidad.localhost:5000"
put_kv "config/controller-service/PERSISTENCE_URL"       "http://persistence-java.universidad.localhost:8080"
put_kv "config/controller-service/REDIS_URL"             "redis://redis:6379"
put_kv "config/controller-service/REQUEST_TIMEOUT"       "60"
# Traefik tags
put_kv "config/controller-service/traefik/enable"        "true"
put_kv "config/controller-service/traefik/router_rule"   "Host(\`api.universidad.localhost\`)"
put_kv "config/controller-service/traefik/entrypoints"   "http,https"
put_kv "config/controller-service/traefik/lb_port"       "5000"
echo ""

# ─── User Service (Python/FastAPI) ───────────────────────────────────────
echo "▸ user-service"
put_kv "config/user-service/HOST"                    "0.0.0.0"
put_kv "config/user-service/PORT"                    "5000"
put_kv "config/user-service/DEBUG"                   "False"
put_kv "config/user-service/LOG_LEVEL"               "INFO"
put_kv "config/user-service/JWT_SECRET_KEY"          "your-super-secret-key-change-in-production"
put_kv "config/user-service/JWT_ALGORITHM"           "HS256"
put_kv "config/user-service/JWT_EXPIRE_MINUTES"      "30"
put_kv "config/user-service/PERSISTENCE_SERVICE_URL" "http://persistence-java.universidad.localhost:8080"
put_kv "config/user-service/REQUEST_TIMEOUT"         "30"
# Traefik tags
put_kv "config/user-service/traefik/enable"          "true"
put_kv "config/user-service/traefik/router_rule"     "Host(\`users.universidad.localhost\`)"
put_kv "config/user-service/traefik/entrypoints"     "http,https"
put_kv "config/user-service/traefik/lb_port"         "5000"
echo ""

# ─── Extract Service (Python/FastAPI) ────────────────────────────────────
echo "▸ extract-service"
put_kv "config/extract-service/HOST"                 "0.0.0.0"
put_kv "config/extract-service/PORT"                 "5000"
# Traefik tags
put_kv "config/extract-service/traefik/enable"       "true"
put_kv "config/extract-service/traefik/router_rule"  "Host(\`extractor.universidad.localhost\`)"
put_kv "config/extract-service/traefik/entrypoints"  "http,https"
put_kv "config/extract-service/traefik/lb_port"      "5000"
echo ""

# ─── Summary Service (Python/FastAPI + Groq) ─────────────────────────────
echo "▸ summary-service"

# Resolve GROQ_API_KEY dynamically to avoid hardcoding secrets in Git
GROQ_API_KEY_VAL="${GROQ_API_KEY:-}"
if [ -z "${GROQ_API_KEY_VAL}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  for env_file in "${SCRIPT_DIR}/../../../Summary-service/.env" "${SCRIPT_DIR}/../../Summary-service/.env" "../../Summary-service/.env"; do
    if [ -f "${env_file}" ]; then
      extracted_key=$(grep -E "^GROQ_API_KEY=" "${env_file}" | cut -d'=' -f2- | tr -d '"'\'' ')
      if [ -n "${extracted_key}" ]; then
        GROQ_API_KEY_VAL="${extracted_key}"
        break
      fi
    fi
  done
fi
if [ -z "${GROQ_API_KEY_VAL}" ]; then
  GROQ_API_KEY_VAL="your-groq-api-key-here"
fi

put_kv "config/summary-service/HOST"                 "0.0.0.0"
put_kv "config/summary-service/PORT"                 "5000"
put_kv "config/summary-service/LOG_LEVEL"            "INFO"
put_kv "config/summary-service/HEALTHCHECK_AI"       "false"
put_kv "config/summary-service/GROQ_API_KEY"         "${GROQ_API_KEY_VAL}"
put_kv "config/summary-service/GROQ_MODEL"           "llama-3.3-70b-versatile"
put_kv "config/summary-service/AI_CONNECT_TIMEOUT_SECONDS"  "10"
put_kv "config/summary-service/AI_REQUEST_TIMEOUT_SECONDS"  "60"
put_kv "config/summary-service/AI_HEALTHCHECK_TIMEOUT_SECONDS" "5"
put_kv "config/summary-service/DEFAULT_MAX_TOKENS"   "2048"
put_kv "config/summary-service/MIN_TEXT_LENGTH"       "100"
put_kv "config/summary-service/REDIS_HOST"           "redis"
put_kv "config/summary-service/REDIS_PORT"           "6379"
# Traefik tags
put_kv "config/summary-service/traefik/enable"       "true"
put_kv "config/summary-service/traefik/router_rule"  "Host(\`ai.universidad.localhost\`)"
put_kv "config/summary-service/traefik/entrypoints"  "http,https"
put_kv "config/summary-service/traefik/lb_port"      "5000"
echo ""

# ─── Persistence Service (Java/Spring Boot) ──────────────────────────────
echo "▸ persistence-service"
put_kv "config/persistence-service/PORT"             "8080"
put_kv "config/persistence-service/DB_WRITE_HOST"    "postgres"
put_kv "config/persistence-service/DB_READ_HOST"     "postgres"
put_kv "config/persistence-service/DB_PORT"          "5432"
put_kv "config/persistence-service/DB_NAME"          "notebookum"
put_kv "config/persistence-service/DB_USER"          "notebookum"
put_kv "config/persistence-service/DB_PASSWORD"      "notebookum123"
put_kv "config/persistence-service/REDIS_HOST"       "redis"
put_kv "config/persistence-service/REDIS_PORT"       "6379"
put_kv "config/persistence-service/ALLOWED_ORIGINS"  "*"
put_kv "config/persistence-service/DDL_AUTO"         "update"
# Traefik tags (nested for Python/Go consul_registration)
put_kv "config/persistence-service/traefik/enable"       "true"
put_kv "config/persistence-service/traefik/router_rule"  "Host(\`persistence-java.universidad.localhost\`)"
put_kv "config/persistence-service/traefik/entrypoints"  "http,https"
put_kv "config/persistence-service/traefik/lb_port"      "8080"
# Traefik tags (flat keys for Spring Cloud Consul config resolution)
put_kv "config/persistence-service/TRAEFIK_ENABLE"       "true"
put_kv "config/persistence-service/TRAEFIK_ROUTER_RULE"  "Host(\`persistence-java.universidad.localhost\`)"
put_kv "config/persistence-service/TRAEFIK_ENTRYPOINTS"  "http,https"
put_kv "config/persistence-service/TRAEFIK_LB_PORT"      "8080"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Configuración cargada exitosamente en Consul KV"
echo "  Verificar en: ${CONSUL_ADDR}/ui"
echo "═══════════════════════════════════════════════════════════"
