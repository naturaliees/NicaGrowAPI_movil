from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings
from django.db import OperationalError
from rest_framework.test import APIClient
from rest_framework.exceptions import NotFound, ValidationError
from .repository import resolve, select_rows

COLUMNS = [
    {'nombre': 'VentaId', 'tipo': 'int', 'nullable': False, 'pk': True},
    {'nombre': 'CiudadId', 'tipo': 'int', 'nullable': False, 'pk': False},
]
@override_settings(API_KEY='test-key', ALLOWED_HOSTS=['testserver'])
class ApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
    def authorize(self):
        self.client.credentials(HTTP_X_API_KEY='test-key')
    def test_authentication(self):
        self.assertEqual(self.client.get('/api/').status_code, 401)
        self.authorize()
        self.assertEqual(len(self.client.get('/api/').data['tablas']), 14)
    def test_unknown_table_is_rejected_before_sql(self):
        self.authorize()
        self.assertEqual(self.client.get('/api/dw/Secretos/').status_code, 404)
        with self.assertRaises(NotFound):
            resolve('dw', 'Fact_Ventas]; DROP TABLE x;--')
    def test_write_methods_not_available(self):
        self.authorize()
        self.assertEqual(self.client.post('/api/dw/Fact_Ventas/', {}).status_code, 405)
    @patch('api.repository.metadata', return_value=COLUMNS)
    def test_invalid_inputs(self, metadata):
        for params in [{'tamano': '501'}, {'pagina': '0'}, {'orden': 'x;DROP'}, {'inventado': 'x'}]:
            with self.assertRaises(ValidationError):
                select_rows('dw', 'Fact_Ventas', params)
    @patch('api.repository.connection')
    @patch('api.repository.metadata', return_value=COLUMNS)
    def test_filters_are_bound_and_pagination_is_stable(self, metadata, conn):
        cursor = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        cursor.fetchone.return_value = [1]
        cursor.fetchall.return_value = [(1, 2)]
        dangerous = "2' OR 1=1--"
        result = select_rows('dw', 'Fact_Ventas', {'CiudadId': dangerous, 'pagina': '2', 'tamano': '10'})
        sql, values = cursor.execute.call_args.args
        self.assertNotIn(dangerous, sql)
        self.assertIn('[dw].[Fact_Ventas]', sql)
        self.assertIn('ORDER BY [VentaId] ASC', sql)
        self.assertEqual(values, [dangerous, 10, 10])
        self.assertEqual(result['datos'], [{'VentaId': 1, 'CiudadId': 2}])
    @patch('api.repository.connection')
    def test_staging_is_unavailable_without_any_database_access(self, conn):
        self.authorize()
        for table in ['Historial_Busqueda', 'Incidentes', 'Tendencia_Temporada', 'Valoracion_Producto', 'Valoracion_Servicio']:
            for suffix in ['', 'estructura/', '1/']:
                response = self.client.get(f'/api/staging/{table}/{suffix}')
                self.assertEqual(response.status_code, 404)
        conn.cursor.assert_not_called()
    def test_duplicate_params(self):
        self.authorize()
        self.assertEqual(self.client.get('/api/dw/Fact_Ventas/?pagina=1&pagina=2').status_code, 400)
    @patch('api.views.select_rows', side_effect=OperationalError('private server details'))
    def test_database_failure_does_not_expose_details(self, query):
        self.authorize()
        response = self.client.get('/api/dw/Fact_Ventas/')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private server details', str(response.data))

class ReportTests(SimpleTestCase):
    def test_dates_and_limits(self):
        from .reports import ReportFilters
        for data in [{'desde': '2026-02-01', 'hasta': '2026-01-01'}, {'limite': 101}, {'desde': 'abc'}]:
            self.assertFalse(ReportFilters(data=data).is_valid())
    def test_decimal_precision(self):
        from .renderers import ExactJSONRenderer
        from decimal import Decimal
        self.assertIn(b'"1234567890123456.78"', ExactJSONRenderer().render({'total': Decimal('1234567890123456.78')}))
    @patch('api.reports.connection')
    def test_report_filter_parameters(self, conn):
        from .reports import report
        cursor = conn.cursor.return_value.__enter__.return_value
        cursor.description = [('producto',)]; cursor.fetchall.return_value = []
        report('top-productos', {'desde': '2026-01-01', 'estado_key': '2', 'limite': '5'})
        sql, values = cursor.execute.call_args.args
        self.assertIn('TOP (%s)', sql)
        self.assertIn('v.EstadoKey = %s', sql)
        self.assertEqual(values[0], 5)
        self.assertEqual(values[-1], 2)

@override_settings(API_KEY='test-key', ALLOWED_HOSTS=['testserver'])
class ResourceTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient(HTTP_X_API_KEY='test-key')
    def test_router_only_has_unmanaged_dw_models(self):
        from .urls import router
        self.assertEqual(len(router.registry), 14)
        for _, viewset, _ in router.registry:
            model = viewset.queryset.model
            self.assertFalse(model._meta.managed)
            self.assertTrue(model._meta.db_table.startswith('[dw].['))
            self.assertEqual(viewset.serializer_class.Meta.read_only_fields, viewset.serializer_class.Meta.fields)
    def test_resource_auth_and_rejected_writes(self):
        self.assertEqual(APIClient().get('/api/productos/').status_code, 401)
        for verb in ['post', 'put', 'patch', 'delete']:
            self.assertEqual(getattr(self.client, verb)('/api/productos/').status_code, 405)
    def test_resource_rejects_bad_filters_before_sql(self):
        for params in [{'orden': 'x;DROP'}, {'ProductoKey': 'invalid'}, {'desconocido': 'x'}, {'ProductoKey': ['1', '2']}]:
            self.assertEqual(self.client.get('/api/productos/', params).status_code, 400)
