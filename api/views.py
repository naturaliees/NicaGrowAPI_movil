from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .catalog import TABLES
from .repository import metadata, select_rows
class CatalogView(APIView):
    def get(self, request):
        from .urls import router
        return Response({'recursos': {prefix: f'/api/{prefix}/' for prefix, _, _ in router.registry}, 'tablas': [{'schema': s, 'tabla': t, 'url': f'/api/{s}/{t}/', 'estructura': f'/api/{s}/{t}/estructura/'} for s, ts in TABLES.items() for t in ts]})
class TableView(APIView):
    def get(self, request, schema, table):
        if any(len(request.query_params.getlist(k)) != 1 for k in request.query_params):
            raise ValidationError('No repitas parámetros de consulta.')
        return Response(select_rows(schema, table, request.query_params))
class StructureView(APIView):
    def get(self, request, schema, table):
        return Response({'schema': schema, 'tabla': table, 'columnas': metadata(schema, table)})
class HealthView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return Response({'estado': 'conectado', 'motor': 'SQL Server'})

class ReportView(APIView):
    def get(self, request, name):
        from .reports import report
        if any(len(request.query_params.getlist(k)) != 1 for k in request.query_params):
            raise ValidationError('No repitas parámetros de consulta.')
        return Response(report(name, request.query_params))

class DetailView(APIView):
    def get(self, request, schema, table, pk):
        from rest_framework.exceptions import NotFound
        columns = metadata(schema, table)
        keys = [c['nombre'] for c in columns if c['pk']]
        if len(keys) != 1:
            raise ValidationError('La consulta por ID requiere una clave primaria simple. Usa filtros en la lista.')
        result = select_rows(schema, table, {keys[0]: str(pk), 'tamano': '1'})
        if not result['datos']:
            raise NotFound('Registro no encontrado.')
        return Response(result['datos'][0])

# Typed resources follow the reference repository's Model / Serializer / ViewSet organization.
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import models, serializers
from .pagination import WarehousePagination

class WarehouseViewSet(ReadOnlyModelViewSet):
    pagination_class = WarehousePagination
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        if any(len(params.getlist(k)) != 1 for k in params):
            raise ValidationError('No repitas parámetros de consulta.')
        fields = {field.name: field for field in queryset.model._meta.fields}
        extra = set(params) - set(fields) - {'pagina', 'tamano', 'orden', 'buscar'}
        if extra:
            raise ValidationError('Parámetros desconocidos: ' + ', '.join(sorted(extra)))
        for name, value in params.items():
            if name not in fields:
                continue
            field = fields[name]
            try:
                target = field.target_field if field.is_relation else field
                converted = target.to_python(value)
            except (DjangoValidationError, ValueError, TypeError, OverflowError):
                raise ValidationError({name: 'Valor incompatible con el tipo de columna.'})
            queryset = queryset.filter(**{name: converted})
        search = params.get('buscar')
        if search:
            text_fields = [f.name for f in fields.values() if f.get_internal_type() in ('CharField', 'TextField')]
            if not text_fields:
                raise ValidationError('Esta tabla no contiene campos de texto para buscar.')
            condition = Q()
            for name in text_fields:
                condition |= Q(**{name + '__icontains': search})
            queryset = queryset.filter(condition)
        ordering = params.get('orden', queryset.model._meta.pk.name)
        name = ordering[1:] if ordering.startswith('-') else ordering
        if name not in fields:
            raise ValidationError('Columna de orden desconocida.')
        keys = [ordering]
        if name != queryset.model._meta.pk.name:
            keys.append(queryset.model._meta.pk.name)
        return queryset.order_by(*keys)


class DimCiudadViewSet(WarehouseViewSet):
    queryset = models.DimCiudad.objects.all()
    serializer_class = serializers.DimCiudadSerializer


class DimClienteViewSet(WarehouseViewSet):
    queryset = models.DimCliente.objects.all()
    serializer_class = serializers.DimClienteSerializer


class DimEstadoViewSet(WarehouseViewSet):
    queryset = models.DimEstado.objects.all()
    serializer_class = serializers.DimEstadoSerializer


class DimMetodoEnvioViewSet(WarehouseViewSet):
    queryset = models.DimMetodoEnvio.objects.all()
    serializer_class = serializers.DimMetodoEnvioSerializer


class DimMetodoPagoViewSet(WarehouseViewSet):
    queryset = models.DimMetodoPago.objects.all()
    serializer_class = serializers.DimMetodoPagoSerializer


class DimProductoViewSet(WarehouseViewSet):
    queryset = models.DimProducto.objects.all()
    serializer_class = serializers.DimProductoSerializer


class DimTemporadaViewSet(WarehouseViewSet):
    queryset = models.DimTemporada.objects.all()
    serializer_class = serializers.DimTemporadaSerializer


class DimTiempoViewSet(WarehouseViewSet):
    queryset = models.DimTiempo.objects.all()
    serializer_class = serializers.DimTiempoSerializer


class DimVendedorViewSet(WarehouseViewSet):
    queryset = models.DimVendedor.objects.all()
    serializer_class = serializers.DimVendedorSerializer


class FactBusquedasViewSet(WarehouseViewSet):
    queryset = models.FactBusquedas.objects.all()
    serializer_class = serializers.FactBusquedasSerializer


class FactIncidentesViewSet(WarehouseViewSet):
    queryset = models.FactIncidentes.objects.all()
    serializer_class = serializers.FactIncidentesSerializer


class FactTendenciaTemporadaViewSet(WarehouseViewSet):
    queryset = models.FactTendenciaTemporada.objects.all()
    serializer_class = serializers.FactTendenciaTemporadaSerializer


class FactValoracionesViewSet(WarehouseViewSet):
    queryset = models.FactValoraciones.objects.all()
    serializer_class = serializers.FactValoracionesSerializer


class FactVentasViewSet(WarehouseViewSet):
    queryset = models.FactVentas.objects.all()
    serializer_class = serializers.FactVentasSerializer
