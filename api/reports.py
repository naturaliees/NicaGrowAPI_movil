from datetime import date
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.db import connection

class ReportFilters(serializers.Serializer):
    desde = serializers.DateField(required=False)
    hasta = serializers.DateField(required=False)
    estado_key = serializers.IntegerField(required=False, min_value=1)
    limite = serializers.IntegerField(required=False, min_value=1, max_value=100, default=10)
    def validate(self, attrs):
        if attrs.get('desde', date.min) > attrs.get('hasta', date.max):
            raise serializers.ValidationError('desde debe ser anterior o igual a hasta.')
        return attrs

QUERIES = {
    'resumen-ventas': '''SELECT COUNT_BIG(*) AS lineas_venta,
        COUNT(DISTINCT v.IdPedidoOrigen) AS pedidos,
        COALESCE(SUM(CAST(v.Cantidad AS bigint)),0) AS unidades,
        COALESCE(SUM(v.ImporteVenta),0) AS importe_total
        FROM dw.Fact_Ventas v JOIN dw.Dim_Tiempo t ON v.TiempoKey=t.TiempoKey {where}''',
    'ventas-mensuales': '''SELECT t.Anio AS anio, t.Mes AS mes,
        SUM(CAST(v.Cantidad AS bigint)) AS unidades, SUM(v.ImporteVenta) AS importe_total,
        COUNT(DISTINCT v.IdPedidoOrigen) AS pedidos
        FROM dw.Fact_Ventas v JOIN dw.Dim_Tiempo t ON v.TiempoKey=t.TiempoKey
        {where} GROUP BY t.Anio,t.Mes ORDER BY t.Anio,t.Mes''',
    'top-productos': '''SELECT TOP (%s) p.ProductoKey AS producto_key, p.NombreProducto AS producto,
        p.Categoria AS categoria, SUM(CAST(v.Cantidad AS bigint)) AS unidades,
        SUM(v.ImporteVenta) AS importe_total
        FROM dw.Fact_Ventas v JOIN dw.Dim_Tiempo t ON v.TiempoKey=t.TiempoKey
        JOIN dw.Dim_Producto p ON v.ProductoKey=p.ProductoKey
        {where} GROUP BY p.ProductoKey,p.NombreProducto,p.Categoria
        ORDER BY unidades DESC,p.ProductoKey''',
    'ventas-ciudad': '''SELECT c.Ciudad AS ciudad, SUM(CAST(v.Cantidad AS bigint)) AS unidades,
        SUM(v.ImporteVenta) AS importe_total, COUNT(DISTINCT v.IdPedidoOrigen) AS pedidos
        FROM dw.Fact_Ventas v JOIN dw.Dim_Tiempo t ON v.TiempoKey=t.TiempoKey
        JOIN dw.Dim_Cliente c ON v.ClienteKey=c.ClienteKey
        {where} GROUP BY c.Ciudad ORDER BY importe_total DESC,c.Ciudad''',
}

def report(name, params):
    if name not in QUERIES:
        raise NotFound('Reporte no disponible.')
    extra = set(params) - set(ReportFilters().fields)
    if extra:
        from rest_framework.exceptions import ValidationError
        raise ValidationError('Parámetros desconocidos: ' + ', '.join(sorted(extra)))
    serializer = ReportFilters(data=params); serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    clauses, values = [], []
    for key, expression in [('desde', 't.Fecha >= %s'), ('hasta', 't.Fecha <= %s'), ('estado_key', 'v.EstadoKey = %s')]:
        if key in data:
            clauses.append(expression); values.append(data[key])
    where = 'WHERE ' + ' AND '.join(clauses) if clauses else ''
    if name == 'top-productos':
        values.insert(0, data['limite'])
    with connection.cursor() as cursor:
        cursor.execute(QUERIES[name].format(where=where), values)
        names = [c[0] for c in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]
