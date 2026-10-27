# NicaGrow_DW — Django REST API

API Python para `localhost / NicaGrow_DW`, organizada en modelos, serializers, ViewSets y DefaultRouter, tomando como referencia https://github.com/naturaliees/NicaGrow_backend. Solo utiliza las 14 tablas del esquema dw. Las tablas staging están excluidas del catálogo, modelos y consultas; sus rutas devuelven 404 sin acceder a la base.

## Ejecutar

Las dependencias están instaladas en `.venv` y `.env` contiene la conexión local con Windows y secretos generados. Desde la carpeta NicaGrow_Django_API del Escritorio:

```powershell
./Iniciar.ps1
```

Escucha en http://127.0.0.1:8000. Ctrl+C detiene el servidor. Otro puerto: `-Puerto 8001`.
Abre `.env` localmente para consultar API_KEY; envíala en el encabezado `X-Api-Key` de cada petición. No publiques ese archivo.

## Organización, siguiendo el repositorio de referencia

- api/models.py: 14 modelos explícitos con columnas y relaciones reales, `managed=False` y tablas `[dw].[...]`.
- api/serializers.py: ModelSerializer para cada modelo, campos explícitos e importes decimales exactos.
- api/views.py: ViewSets de lectura para cada recurso; consultas de estructura, salud y reportes.
- api/urls.py: DefaultRouter y registro de recursos.
- api/pagination.py: paginación compartida.
- api/reports.py: agregaciones SQL parametrizadas sobre ventas y dimensiones.
- api/catalog.py y api/repository.py: catálogo permitido y consultas de estructura/rutas técnicas.
- config/settings.py: conexión, autenticación y configuración.

La referencia usa una base transaccional con pedidos, credenciales y registro de usuarios. Aquí los modelos corresponden a tu almacén NicaGrow_DW; no se agregan tablas de credenciales ni procedimientos de pedidos ajenos a ese esquema. Esta API es de consulta (GET, HEAD y OPTIONS); POST, PUT, PATCH y DELETE responden 405. No ejecutes migrate: las tablas existen y las mantiene tu proceso de carga.

## Endpoints

Todas las rutas de recurso permiten lista y detalle `/{id}/`. El id es la clave del almacén (por ejemplo ProductoKey o VentaKey), no el identificador de origen.

| Recurso GET | Tabla |
| --- | --- |
| /api/ciudades/ | dw.Dim_Ciudad |
| /api/clientes/ | dw.Dim_Cliente |
| /api/estados/ | dw.Dim_Estado |
| /api/metodos-envio/ | dw.Dim_Metodo_Envio |
| /api/metodos-pago/ | dw.Dim_Metodo_Pago |
| /api/productos/ | dw.Dim_Producto |
| /api/temporadas/ | dw.Dim_Temporada |
| /api/tiempos/ | dw.Dim_Tiempo |
| /api/vendedores/ | dw.Dim_Vendedor |
| /api/busquedas/ | dw.Fact_Busquedas |
| /api/incidentes/ | dw.Fact_Incidentes |
| /api/tendencias/ | dw.Fact_Tendencia_Temporada |
| /api/valoraciones/ | dw.Fact_Valoraciones |
| /api/ventas/ | dw.Fact_Ventas |

`/api/` muestra catálogo y recursos. `/api/health/` comprueba SQL Server.
Se conservan las rutas técnicas `/api/dw/{tabla}/`, `/api/dw/{tabla}/{id}/` y `/api/dw/{tabla}/estructura/`. Esta última muestra nombres, tipos, nulabilidad y clave primaria. Todos los accesos al esquema staging están bloqueados.

## Filtros y paginación

En los nuevos recursos: `pagina` (desde 1 hasta 100000), `tamano` (1..500; predeterminado 100), `orden` (nombre de columna, con `-` para descendente) y `buscar` (coincidencia parcial en campos de texto). También puedes filtrar por igualdad usando el nombre exacto de cualquier campo del modelo. Las claves foráneas se expresan con su nombre SQL (por ejemplo ProductoKey), sin sufijo `_id`. No se permiten parámetros desconocidos o repetidos.

```text
/api/productos/?buscar=cafe&tamano=20
/api/productos/1/
/api/ventas/?ProductoKey=1&orden=-VentaKey
/api/ventas/?EstadoKey=2&pagina=1&tamano=50
/api/dw/Fact_Ventas/estructura/
```

Las listas responden `{pagina, tamano, total, datos}`. Las rutas técnicas conservan además `paginacion_estable` y `advertencia`. Las claves primarias aseguran desempate en la ordenación; un ETL concurrente puede cambiar el conteo y el contenido entre consultas. Los importes decimales son cadenas JSON para preservar precisión; fechas ISO; relaciones como IDs.

## Reportes para Power BI

| GET | Resultado |
| --- | --- |
| /api/reportes/resumen-ventas/ | Importe, unidades, pedidos distintos y líneas de venta |
| /api/reportes/ventas-mensuales/ | Ventas por año y mes |
| /api/reportes/top-productos/ | Productos ordenados por unidades vendidas |
| /api/reportes/ventas-ciudad/ | Ventas por ciudad del cliente |

Filtros: `desde=2026-01-01`, `hasta=2026-12-31` (fechas inclusivas), `estado_key=2`. En top-productos, `limite=10` (1..100). Sin estado_key se incluyen todos los estados de Fact_Ventas; consulta `/api/estados/` para elegir el adecuado. Las ciudades proceden de Dim_Cliente. Los pedidos distintos de grupos diferentes no son necesariamente sumables.

Los reportes devuelven arrays planos. Power Query:

```powerquery
let
    Fuente = Json.Document(Web.Contents("http://127.0.0.1:8000", [
        RelativePath="api/reportes/ventas-mensuales/",
        Headers=[#"X-Api-Key"="REEMPLAZA_CON_TU_CLAVE"]
    ])),
    Tabla = Table.FromRecords(Fuente),
    Tipos = Table.TransformColumnTypes(Tabla, {{"importe_total", Currency.Type}}, "en-US")
in
    Tipos
```

Usa autenticación Anónima para la URL porque la clave viaja en el encabezado. Protege el PBIX que contiene esa credencial. Power BI Service requiere un gateway o un servidor accesible para actualizar datos locales.

## Ejemplo PowerShell

Dentro de NicaGrow_Django_API, con el servidor iniciado:

```powershell
$lineaClave = Get-Content .env | Where-Object { $_ -like 'API_KEY=*' }
$claveApi = $lineaClave.Substring(8)
Invoke-RestMethod 'http://127.0.0.1:8000/api/productos/?tamano=5' -Headers @{'X-Api-Key'=$claveApi}
```

## Instalación en otro equipo

Requiere Python 3.12, SQL Server y Microsoft ODBC Driver 18 for SQL Server.

```powershell
cd "$([Environment]::GetFolderPath('Desktop'))\NicaGrow_Django_API"
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
# Edita .env: conexión y dos secretos aleatorios propios.
./Iniciar.ps1
```

DB_USER y DB_PASSWORD vacíos usan autenticación Windows. Para autenticación SQL rellena ambos. El servidor predeterminado es localhost, base NicaGrow_DW y puerto vacío para la instancia predeterminada. La configuración local acepta el certificado del servidor (`TrustServerCertificate=yes`); en despliegue configura un certificado válido y cambia a `no`. Usa HTTPS y permisos de lectura. La API key sirve para integraciones privadas; una app móvil pública requiere autenticación y permisos por usuario.

## Verificación

```powershell
./.venv/Scripts/python.exe manage.py check
./.venv/Scripts/python.exe manage.py test api
./.venv/Scripts/python.exe verificar_conexion.py
```

Verificado: revisión Django sin incidencias; 14 pruebas automatizadas; consultas reales a las 14 tablas dw, detalles, filtros y cuatro reportes; los 14 ViewSets y serializers respondieron correctamente. Fact_Ventas tiene 144 filas y el importe del reporte coincide con SUM(ImporteVenta). Las rutas staging devuelven 404 sin consultar SQL. La integración usa el cliente de pruebas Django contra SQL Server, sin depender de un servidor HTTP externo.

`generar_modelos_dw.py` permite regenerar modelos y serializers desde metadatos reales exclusivamente de dw; sobrescribe esos dos archivos, por lo que debe usarse solo cuando cambie la estructura SQL y revisando el resultado.



## Preparación para Azure App Service

El código ya incluye configuración de producción, Gunicorn, HTTPS, dominio de Azure automático y endpoint /healthz/. Consulta [azure/README.md](azure/README.md) para desplegar. Paquete generado: dist/NicaGrow_Azure.zip (sin secretos). Preparación validada con 19 pruebas; esto no confirma todavía una publicación en Azure ni la ejecución de la imagen Linux.
