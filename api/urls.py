from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('ciudades', views.DimCiudadViewSet, basename='ciudades')
router.register('clientes', views.DimClienteViewSet, basename='clientes')
router.register('estados', views.DimEstadoViewSet, basename='estados')
router.register('metodos-envio', views.DimMetodoEnvioViewSet, basename='metodos-envio')
router.register('metodos-pago', views.DimMetodoPagoViewSet, basename='metodos-pago')
router.register('productos', views.DimProductoViewSet, basename='productos')
router.register('temporadas', views.DimTemporadaViewSet, basename='temporadas')
router.register('tiempos', views.DimTiempoViewSet, basename='tiempos')
router.register('vendedores', views.DimVendedorViewSet, basename='vendedores')
router.register('busquedas', views.FactBusquedasViewSet, basename='busquedas')
router.register('incidentes', views.FactIncidentesViewSet, basename='incidentes')
router.register('tendencias', views.FactTendenciaTemporadaViewSet, basename='tendencias')
router.register('valoraciones', views.FactValoracionesViewSet, basename='valoraciones')
router.register('ventas', views.FactVentasViewSet, basename='ventas')

urlpatterns = router.urls
