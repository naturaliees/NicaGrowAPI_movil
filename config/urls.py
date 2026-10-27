from django.urls import path, include
from config.health import healthz
from api.views import CatalogView, TableView, StructureView, HealthView, ReportView, DetailView
urlpatterns = [
    path('healthz/', healthz),
    path('api/', CatalogView.as_view()),
    path('api/health/', HealthView.as_view()),
    path('api/reportes/<slug:name>/', ReportView.as_view()),
    path('api/', include('api.urls')),
    path('api/<str:schema>/<str:table>/estructura/', StructureView.as_view()),
    path('api/<str:schema>/<str:table>/<int:pk>/', DetailView.as_view()),
    path('api/<str:schema>/<str:table>/', TableView.as_view()),
]
