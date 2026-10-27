# Conexión a Azure SQL

La API está configurada para el servidor nicagrowazure.database.windows.net, base nicagrow_dw, puerto 1433 y usuario SQL NicaGrowADM.

1. Abre .env y establece DB_PASSWORD con tu contraseña nueva. No la incluyas en código ni en Git.
2. En Azure, la red del servidor SQL debe permitir la conexión desde tu equipo (si usas acceso público, autoriza solamente tu IP cliente).
3. Reinicia el servidor de Django en PyCharm después de modificar .env.
4. Ejecuta `.\.venv\Scripts\python.exe verificar_conexion.py` para verificar los recursos dw y los reportes contra Azure SQL.

No cambies Encrypt=yes ni TrustServerCertificate=no. Solo se consultan las 14 tablas dw; staging sigue excluido. Las tablas y datos deben existir en la base de Azure: la configuración no los migra.

Esta modificación conecta la API ejecutada en tu equipo a Azure SQL. No publica el backend en App Service. Para desplegarlo, configura estas mismas variables como ajustes de Azure, los secretos, el dominio permitido, el servidor WSGI y las dependencias de Linux. No publiques .env ni .venv.
