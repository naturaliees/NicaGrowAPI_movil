param([int]$Puerto = 8000)
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Primero crea .venv e instala requirements.lock.txt. Consulta README.md.' }
& $python (Join-Path $PSScriptRoot 'manage.py') runserver "127.0.0.1:$Puerto" --noreload
