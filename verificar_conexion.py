"""Read-only integration verification against the configured SQL Server."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from decimal import Decimal
from django.conf import settings
from django.db import connection
from rest_framework.test import APIClient
from api.catalog import TABLES
client = APIClient(HTTP_HOST='localhost')
client.credentials(HTTP_X_API_KEY=settings.API_KEY)
for schema, tables in TABLES.items():
    for table in tables:
        path = f'/api/{schema}/{table}/'
        structure = client.get(path + 'estructura/')
        assert structure.status_code == 200, (path, structure.data)
        response = client.get(path, {'tamano': 2})
        assert response.status_code == 200, (path, response.data)
        print(f'{schema}.{table}: {response.data["total"]} filas')
        keys = [c['nombre'] for c in structure.data['columnas'] if c['pk']]
        if len(keys) == 1 and response.data['datos']:
            pk = response.data['datos'][0][keys[0]]
            detail = client.get(path + str(pk) + '/')
            assert detail.status_code == 200, detail.data
        if response.data['datos']:
            first = structure.data['columnas'][0]['nombre']
            filtered = client.get(path, {first: response.data['datos'][0][first]})
            assert filtered.status_code == 200, filtered.data
            assert filtered.data['total'] >= 1
for name in ['resumen-ventas', 'ventas-mensuales', 'top-productos', 'ventas-ciudad']:
    r = client.get(f'/api/reportes/{name}/')
    assert r.status_code == 200, (name, r.data)
    print(f'Reporte {name}: OK ({len(r.data)} filas)')
summary = client.get('/api/reportes/resumen-ventas/').data[0]
with connection.cursor() as cursor:
    cursor.execute('SELECT COUNT_BIG(*), COALESCE(SUM(ImporteVenta),0) FROM dw.Fact_Ventas')
    count, amount = cursor.fetchone()
assert summary['lineas_venta'] == count
assert Decimal(str(summary['importe_total'])) == amount
assert client.get('/api/reportes/ventas-mensuales/', {'desde': '2026-02-01', 'hasta': '2026-01-01'}).status_code == 400
assert client.get('/api/health/').status_code == 200
print('OK: tablas, estructuras, filtros, detalles, reportes y total de ventas verificados.')

# Verify typed resources registered through the same DRF router used by the API.
from api.urls import router
from django.db import models
for prefix, viewset, basename in router.registry:
    model = viewset.queryset.model
    assert model._meta.db_table.startswith('[dw].[')
    assert not model._meta.managed
    response = client.get(f'/api/{prefix}/', {'tamano': 2})
    assert response.status_code == 200, (prefix, response.data)
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT_BIG(*) FROM ' + model._meta.db_table)
        expected = cursor.fetchone()[0]
    assert response.data['total'] == expected
    if response.data['datos']:
        first = response.data['datos'][0]
        pk = first[model._meta.pk.name]
        detail = client.get(f'/api/{prefix}/{pk}/')
        assert detail.status_code == 200, (prefix, detail.data)
        assert detail.data == first
        filtered = client.get(f'/api/{prefix}/', {model._meta.pk.name: pk})
        assert filtered.status_code == 200 and filtered.data['total'] == 1
    assert client.post(f'/api/{prefix}/', {}, format='json').status_code == 405
    print(f'Recurso ORM {prefix}: OK')
for suffix in ['', 'estructura/', '1/']:
    assert client.get('/api/staging/Incidentes/' + suffix).status_code == 404
print('OK: 14 recursos ORM; staging no está disponible.')
