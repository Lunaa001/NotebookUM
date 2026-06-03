#!/bin/bash

# Simple HTTP server to serve the dashboard
# Usage: ./serve-dashboard.sh

PORT=${1:-3000}

echo "🚀 Sirviendo Dashboard en http://localhost:$PORT"
echo "   Abre en tu navegador: http://localhost:$PORT/dashboard.html"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

python3 -m http.server $PORT
