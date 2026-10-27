# Despliegue de NicaGrow en Azure App Service

Estado: código preparado para despliegue; publicación y ejecución en Linux requieren validación en tu cuenta. Los recursos dw son de lectura. No se incluyen staging, migraciones ni cambios de datos.

## 1. Aplicación de Azure

Usa una Web App de App Service para Linux, publicación de código y Python 3.12. Si no tienes una, créala en el portal eligiendo tu suscripción, región y plan. El plan puede tener costo; los scripts de esta carpeta nunca crean recursos automáticamente. Si ya tienes una app, usa sus nombres exactos de aplicación y grupo de recursos.

## 2. Variables de entorno

En el portal, dentro de la Web App, abre Configuración > Variables de entorno (los nombres pueden variar con el idioma del portal). Agrega y guarda:

| Variable | Valor |
| --- | --- |
| APP_ENV | production |
| DJANGO_DEBUG | false |
| DB_HOST | nicagrowazure.database.windows.net |
| DB_PORT | 1433 |
| DB_NAME | nicagrow_dw |
| DB_USER | NicaGrowADM |
| DB_PASSWORD | Tu contraseña nueva de Azure SQL |
| DB_PYTHON_DRIVER | mssql_python |
| DB_EXTRA_PARAMS | Encrypt=yes;TrustServerCertificate=no |
| DJANGO_SECRET_KEY | Un secreto aleatorio de al menos 32 caracteres |
| API_KEY | Una clave aleatoria de al menos 32 caracteres |
| SCM_DO_BUILD_DURING_DEPLOYMENT | true |
| DISABLE_COLLECTSTATIC | true |

No subas .env. Las variables de Azure prevalecen y .env no se carga en producción. Puedes copiar los secretos locales si son adecuados y privados o generar otros con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Si cambias API_KEY, actualiza tus integraciones. El dominio asignado por App Service se añade automáticamente desde WEBSITE_HOSTNAME. Para dominios propios, añade DJANGO_ALLOWED_HOSTS con los hosts exactos separados por comas. Nunca uses *.

appsettings.example.json es solo una referencia sin secretos; sustituye sus marcadores antes de importarlo. No contiene credenciales reales.

## 3. Acceso a SQL

Autorizar tu IP del hogar no autoriza la Web App. En el servidor Azure SQL configura el acceso de red para la Web App: por ejemplo, sus direcciones de salida en reglas de firewall concretas, o una red privada con integración de red y DNS. Los cambios de plan pueden modificar las IP de salida. No habilites acceso general a todas las IP ni a todos los servicios Azure para resolverlo. El script no modifica el firewall. Para producción es preferible un usuario de solo lectura limitado a dw en vez del administrador del servidor.

## 4. Publicar desde Windows

Instala Azure CLI, ejecuta `az login` y selecciona la suscripción correcta con `az account set --subscription TU_ID` si tienes varias. Desde la carpeta del proyecto:

```powershell
./azure/Desplegar.ps1 -GrupoRecursos 'TU_GRUPO' -NombreApp 'TU_APP'
```

El script requiere una app Linux existente y que los tres secretos ya estén configurados. Prepara el ZIP, configura Python 3.12, arranque `sh startup.sh`, HTTPS y health check `/healthz/`, y envía el código. No crea recursos, no copia contraseñas locales y no modifica tablas. Un despliegue correcto debe confirmarse con las pruebas del paso 5.

El archivo `dist/NicaGrow_Azure.zip` se construye con una lista explícita de archivos permitidos: api, config, manage.py y dependencias/arranque. Excluye .env, .venv, .idea, caches y contraseñas. Puede regenerarse con:

```powershell
./.venv/Scripts/python.exe azure/empaquetar.py
```

Si no instalas Azure CLI, puedes subir el ZIP a Azure Cloud Shell y usar `az webapp deploy --resource-group TU_GRUPO --name TU_APP --src-path NicaGrow_Azure.zip --type zip` después de configurar las variables, Python, HTTPS, health check y arranque en el portal.

## 5. Comprobar tras publicar

1. Visita `https://TU_DOMINIO/healthz/`: debe responder 200 con estado activo. Solo comprueba el proceso, sin revelar datos ni consultar SQL.
2. En Postman usa GET `https://TU_DOMINIO/api/health/`, encabezado X-Api-Key: debe responder conectado.
3. Prueba `/api/productos/`, `/api/ventas/` y `/api/reportes/resumen-ventas/` con el mismo encabezado.
4. Confirma que las solicitudes sin clave devuelven 401 y que `/api/staging/Incidentes/` devuelve 404 con la clave correcta.
5. Cambia la URL base de la app móvil a `https://TU_DOMINIO/api/`. La clave compartida es para integraciones privadas; no sustituye login y autorización de usuarios en una app móvil pública.

## Diagnóstico

- DisallowedHost: revisa WEBSITE_HOSTNAME y los dominios permitidos.
- Falta una variable/secreto: configura las variables de entorno, guarda y reinicia la app.
- 503 en /api/health/: revisa credenciales, nombre de base y firewall de SQL. No desactives TLS.
- Error al importar mssql_python: faltan bibliotecas nativas de Linux. El controlador incluye Microsoft ODBC 18, pero requiere libltdl7, libkrb5-3 y libgssapi-krb5-2. El Dockerfile opcional instala estas bibliotecas en una imagen Debian/Python 3.12. Si la imagen administrada de App Service no las proporciona, usa esa imagen como contenedor tras construirla y publicarla en tu registro. No se ha construido el contenedor en este equipo.
- Para logs: `az webapp log tail --resource-group TU_GRUPO --name TU_APP` (habilita logs del contenedor si hace falta).

No se ejecuta collectstatic porque la API devuelve JSON y no sirve una interfaz estática. No se ejecutan migraciones. Gunicorn sirve la aplicación con dos workers; las bibliotecas para Windows no se copian.

Referencias: https://learn.microsoft.com/en-us/azure/app-service/configure-language-python y https://github.com/microsoft/mssql-django#selecting-the-database-driver y https://learn.microsoft.com/en-us/sql/connect/python/mssql-python/installation
