param(
    [Parameter(Mandatory=$true)][string]$GrupoRecursos,
    [Parameter(Mandatory=$true)][string]$NombreApp
)
$ErrorActionPreference = 'Stop'
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Instala Azure CLI y ejecuta az login antes de desplegar. Consulta azure/README.md.'
}
function Invoke-Azure {
    param([string[]]$Arguments)
    $result = & az @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'Falló un comando de Azure; revisa el mensaje anterior.' }
    return $result
}
$projectPath = Split-Path $PSScriptRoot -Parent
# This script only targets an existing App Service; it never creates paid resources.
$appJson = Invoke-Azure -Arguments @('webapp','show','--resource-group',$GrupoRecursos,'--name',$NombreApp,'--output','json')
$app = ($appJson -join "`n") | ConvertFrom-Json
if (!$app.reserved) { throw 'La aplicación debe ser App Service para Linux.' }
$namesJson = Invoke-Azure -Arguments @('webapp','config','appsettings','list','--resource-group',$GrupoRecursos,'--name',$NombreApp,'--query','[].name','--output','json')
$names = ($namesJson -join "`n") | ConvertFrom-Json
foreach ($required in @('DB_PASSWORD','DJANGO_SECRET_KEY','API_KEY')) {
    if ($required -notin $names) { throw "Configura $required en las variables de entorno del App Service antes de continuar." }
}
$python = Join-Path $projectPath '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $python)) { throw 'No se encontró el entorno Python local.' }
& $python (Join-Path $PSScriptRoot 'empaquetar.py')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar el ZIP.' }
$zip = Join-Path $projectPath 'dist/NicaGrow_Azure.zip'
Invoke-Azure -Arguments @('webapp','config','appsettings','set','--resource-group',$GrupoRecursos,'--name',$NombreApp,'--settings',
    'APP_ENV=production','DJANGO_DEBUG=false','DB_HOST=nicagrowazure.database.windows.net','DB_PORT=1433',
    'DB_NAME=nicagrow_dw','DB_USER=NicaGrowADM','DB_PYTHON_DRIVER=mssql_python',
    'DB_EXTRA_PARAMS=Encrypt=yes;TrustServerCertificate=no','SCM_DO_BUILD_DURING_DEPLOYMENT=true',
    'DISABLE_COLLECTSTATIC=true','--output','none') | Out-Null
Invoke-Azure -Arguments @('webapp','config','set','--resource-group',$GrupoRecursos,'--name',$NombreApp,
    '--linux-fx-version','PYTHON|3.12','--startup-file','sh startup.sh','--output','none') | Out-Null
Invoke-Azure -Arguments @('webapp','update','--resource-group',$GrupoRecursos,'--name',$NombreApp,
    '--https-only','true','--output','none') | Out-Null
Invoke-Azure -Arguments @('resource','update','--ids',$app.id,'--set','properties.siteConfig.healthCheckPath=/healthz/','--output','none') | Out-Null
Invoke-Azure -Arguments @('webapp','deploy','--resource-group',$GrupoRecursos,'--name',$NombreApp,
    '--src-path',$zip,'--type','zip','--output','none') | Out-Null
Write-Output "Código enviado. Verifica https://$($app.defaultHostName)/healthz/ y /api/health/ con X-Api-Key."
