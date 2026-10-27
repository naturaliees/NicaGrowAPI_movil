import logging
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler
logger = logging.getLogger(__name__)
def exception_handler(exc, context):
    if isinstance(exc, DatabaseError):
        logger.exception('Error al consultar SQL Server')
        return Response({'detail': 'No fue posible consultar SQL Server. Revisa la conexión y los permisos.'}, status=503)
    return drf_handler(exc, context)
