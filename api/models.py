"""Existing NicaGrow_DW dimensions and facts; Django does not manage DDL."""
from django.db import models

class DimCiudad(models.Model):
    CiudadKey = models.AutoField(db_column='CiudadKey', primary_key=True)
    CiudadID = models.CharField(db_column='CiudadID', max_length=3)
    Ciudad = models.CharField(db_column='Ciudad', max_length=50)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Ciudad]"

class DimCliente(models.Model):
    ClienteKey = models.AutoField(db_column='ClienteKey', primary_key=True)
    IdClienteOrigen = models.IntegerField(db_column='IdClienteOrigen')
    NombreCompleto = models.CharField(db_column='NombreCompleto', max_length=101)
    Ciudad = models.CharField(db_column='Ciudad', null=True, blank=True, max_length=50)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Cliente]"

class DimEstado(models.Model):
    EstadoKey = models.AutoField(db_column='EstadoKey', primary_key=True)
    IdEstadoOrigen = models.IntegerField(db_column='IdEstadoOrigen')
    TipoEstado = models.CharField(db_column='TipoEstado', max_length=50)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Estado]"

class DimMetodoEnvio(models.Model):
    MetodoEnvioKey = models.AutoField(db_column='MetodoEnvioKey', primary_key=True)
    IdMetodoEnvioOrigen = models.IntegerField(db_column='IdMetodoEnvioOrigen')
    MetodoEnvio = models.CharField(db_column='MetodoEnvio', max_length=100)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Metodo_Envio]"

class DimMetodoPago(models.Model):
    MetodoPagoKey = models.AutoField(db_column='MetodoPagoKey', primary_key=True)
    IdMetodoPagoOrigen = models.IntegerField(db_column='IdMetodoPagoOrigen')
    Metodo = models.CharField(db_column='Metodo', max_length=100)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Metodo_Pago]"

class DimProducto(models.Model):
    ProductoKey = models.AutoField(db_column='ProductoKey', primary_key=True)
    IdProductoOrigen = models.IntegerField(db_column='IdProductoOrigen')
    NombreProducto = models.CharField(db_column='NombreProducto', max_length=100)
    Categoria = models.CharField(db_column='Categoria', max_length=100)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Producto]"

class DimTemporada(models.Model):
    TemporadaKey = models.AutoField(db_column='TemporadaKey', primary_key=True)
    TemporadaID = models.IntegerField(db_column='TemporadaID')
    NombreTemporada = models.CharField(db_column='NombreTemporada', max_length=100)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Temporada]"

class DimTiempo(models.Model):
    TiempoKey = models.AutoField(db_column='TiempoKey', primary_key=True)
    Fecha = models.DateField(db_column='Fecha')
    Dia = models.IntegerField(db_column='Dia')
    Mes = models.IntegerField(db_column='Mes')
    Anio = models.IntegerField(db_column='Anio')

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Tiempo]"

class DimVendedor(models.Model):
    VendedorKey = models.AutoField(db_column='VendedorKey', primary_key=True)
    IdVendedorOrigen = models.IntegerField(db_column='IdVendedorOrigen')
    NombreCompleto = models.CharField(db_column='NombreCompleto', max_length=101)
    NombreNegocio = models.CharField(db_column='NombreNegocio', max_length=100)
    Ciudad = models.CharField(db_column='Ciudad', null=True, blank=True, max_length=50)

    class Meta:
        managed = False
        db_table = "[dw].[Dim_Vendedor]"

class FactBusquedas(models.Model):
    BusquedaKey = models.BigAutoField(db_column='BusquedaKey', primary_key=True)
    IdBusquedaOrigen = models.IntegerField(db_column='IdBusquedaOrigen')
    TiempoKey = models.ForeignKey('DimTiempo', on_delete=models.DO_NOTHING, db_column='TiempoKey')
    ClienteKey = models.ForeignKey('DimCliente', on_delete=models.DO_NOTHING, db_column='ClienteKey')
    ProductoKey = models.ForeignKey('DimProducto', on_delete=models.DO_NOTHING, db_column='ProductoKey')
    CantidadResultados = models.IntegerField(db_column='CantidadResultados')

    class Meta:
        managed = False
        db_table = "[dw].[Fact_Busquedas]"

class FactIncidentes(models.Model):
    IncidenteKey = models.BigAutoField(db_column='IncidenteKey', primary_key=True)
    IdIncidenteOrigen = models.IntegerField(db_column='IdIncidenteOrigen')
    PedidoOrigen = models.IntegerField(db_column='PedidoOrigen')
    TiempoKey = models.ForeignKey('DimTiempo', on_delete=models.DO_NOTHING, db_column='TiempoKey')
    ClienteKey = models.ForeignKey('DimCliente', on_delete=models.DO_NOTHING, db_column='ClienteKey')
    ProductoKey = models.ForeignKey('DimProducto', on_delete=models.DO_NOTHING, db_column='ProductoKey')
    CiudadKey = models.ForeignKey('DimCiudad', on_delete=models.DO_NOTHING, db_column='CiudadKey')
    MetodoEnvioKey = models.ForeignKey('DimMetodoEnvio', on_delete=models.DO_NOTHING, db_column='MetodoEnvioKey')
    CantidadIncidentes = models.IntegerField(db_column='CantidadIncidentes')

    class Meta:
        managed = False
        db_table = "[dw].[Fact_Incidentes]"

class FactTendenciaTemporada(models.Model):
    TendenciaKey = models.BigAutoField(db_column='TendenciaKey', primary_key=True)
    IdTendenciaOrigen = models.IntegerField(db_column='IdTendenciaOrigen')
    TemporadaKey = models.ForeignKey('DimTemporada', on_delete=models.DO_NOTHING, db_column='TemporadaKey')
    ProductoKey = models.ForeignKey('DimProducto', on_delete=models.DO_NOTHING, db_column='ProductoKey')
    CantidadBusqueda = models.IntegerField(db_column='CantidadBusqueda')
    CantidadPedidos = models.IntegerField(db_column='CantidadPedidos')

    class Meta:
        managed = False
        db_table = "[dw].[Fact_Tendencia_Temporada]"

class FactValoraciones(models.Model):
    ValoracionKey = models.BigAutoField(db_column='ValoracionKey', primary_key=True)
    IdValoracionOrigen = models.IntegerField(db_column='IdValoracionOrigen')
    TiempoKey = models.ForeignKey('DimTiempo', on_delete=models.DO_NOTHING, db_column='TiempoKey')
    ClienteKey = models.ForeignKey('DimCliente', on_delete=models.DO_NOTHING, db_column='ClienteKey')
    ProductoKey = models.ForeignKey('DimProducto', on_delete=models.DO_NOTHING, db_column='ProductoKey', null=True, blank=True)
    MetodoEnvioKey = models.ForeignKey('DimMetodoEnvio', on_delete=models.DO_NOTHING, db_column='MetodoEnvioKey', null=True, blank=True)
    Calificacion = models.IntegerField(db_column='Calificacion')

    class Meta:
        managed = False
        db_table = "[dw].[Fact_Valoraciones]"

class FactVentas(models.Model):
    VentaKey = models.BigAutoField(db_column='VentaKey', primary_key=True)
    IdDetalleOrigen = models.IntegerField(db_column='IdDetalleOrigen')
    IdPedidoOrigen = models.IntegerField(db_column='IdPedidoOrigen')
    TiempoKey = models.ForeignKey('DimTiempo', on_delete=models.DO_NOTHING, db_column='TiempoKey')
    ClienteKey = models.ForeignKey('DimCliente', on_delete=models.DO_NOTHING, db_column='ClienteKey')
    ProductoKey = models.ForeignKey('DimProducto', on_delete=models.DO_NOTHING, db_column='ProductoKey')
    VendedorKey = models.ForeignKey('DimVendedor', on_delete=models.DO_NOTHING, db_column='VendedorKey')
    EstadoKey = models.ForeignKey('DimEstado', on_delete=models.DO_NOTHING, db_column='EstadoKey')
    MetodoPagoKey = models.ForeignKey('DimMetodoPago', on_delete=models.DO_NOTHING, db_column='MetodoPagoKey')
    MetodoEnvioKey = models.ForeignKey('DimMetodoEnvio', on_delete=models.DO_NOTHING, db_column='MetodoEnvioKey')
    Cantidad = models.IntegerField(db_column='Cantidad')
    PrecioUnitario = models.DecimalField(db_column='PrecioUnitario', max_digits=10, decimal_places=2)
    ImporteVenta = models.DecimalField(db_column='ImporteVenta', max_digits=18, decimal_places=2)

    class Meta:
        managed = False
        db_table = "[dw].[Fact_Ventas]"
