from rest_framework import serializers
from . import models

class DimCiudadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimCiudad
        fields = ['CiudadKey', 'CiudadID', 'Ciudad']
        read_only_fields = fields

class DimClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimCliente
        fields = ['ClienteKey', 'IdClienteOrigen', 'NombreCompleto', 'Ciudad']
        read_only_fields = fields

class DimEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimEstado
        fields = ['EstadoKey', 'IdEstadoOrigen', 'TipoEstado']
        read_only_fields = fields

class DimMetodoEnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimMetodoEnvio
        fields = ['MetodoEnvioKey', 'IdMetodoEnvioOrigen', 'MetodoEnvio']
        read_only_fields = fields

class DimMetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimMetodoPago
        fields = ['MetodoPagoKey', 'IdMetodoPagoOrigen', 'Metodo']
        read_only_fields = fields

class DimProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimProducto
        fields = ['ProductoKey', 'IdProductoOrigen', 'NombreProducto', 'Categoria']
        read_only_fields = fields

class DimTemporadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimTemporada
        fields = ['TemporadaKey', 'TemporadaID', 'NombreTemporada']
        read_only_fields = fields

class DimTiempoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimTiempo
        fields = ['TiempoKey', 'Fecha', 'Dia', 'Mes', 'Anio']
        read_only_fields = fields

class DimVendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DimVendedor
        fields = ['VendedorKey', 'IdVendedorOrigen', 'NombreCompleto', 'NombreNegocio', 'Ciudad']
        read_only_fields = fields

class FactBusquedasSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FactBusquedas
        fields = ['BusquedaKey', 'IdBusquedaOrigen', 'TiempoKey', 'ClienteKey', 'ProductoKey', 'CantidadResultados']
        read_only_fields = fields

class FactIncidentesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FactIncidentes
        fields = ['IncidenteKey', 'IdIncidenteOrigen', 'PedidoOrigen', 'TiempoKey', 'ClienteKey', 'ProductoKey', 'CiudadKey', 'MetodoEnvioKey', 'CantidadIncidentes']
        read_only_fields = fields

class FactTendenciaTemporadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FactTendenciaTemporada
        fields = ['TendenciaKey', 'IdTendenciaOrigen', 'TemporadaKey', 'ProductoKey', 'CantidadBusqueda', 'CantidadPedidos']
        read_only_fields = fields

class FactValoracionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FactValoraciones
        fields = ['ValoracionKey', 'IdValoracionOrigen', 'TiempoKey', 'ClienteKey', 'ProductoKey', 'MetodoEnvioKey', 'Calificacion']
        read_only_fields = fields

class FactVentasSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FactVentas
        fields = ['VentaKey', 'IdDetalleOrigen', 'IdPedidoOrigen', 'TiempoKey', 'ClienteKey', 'ProductoKey', 'VendedorKey', 'EstadoKey', 'MetodoPagoKey', 'MetodoEnvioKey', 'Cantidad', 'PrecioUnitario', 'ImporteVenta']
        read_only_fields = fields
