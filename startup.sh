#!/bin/sh
set -eu
# The working directory is the deployed project root (next to manage.py).
python -c "import mssql_python" || { echo "Faltan dependencias Linux del controlador. Consulta azure/README.md." >&2; exit 1; }
python manage.py check --deploy --fail-level WARNING
exec python -m gunicorn --config gunicorn.conf.py config.wsgi:application
