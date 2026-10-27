from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

class WarehousePagination(PageNumberPagination):
    page_size = 100
    page_query_param = 'pagina'
    page_size_query_param = 'tamano'
    max_page_size = 500

    def paginate_queryset(self, queryset, request, view=None):
        try:
            page = int(request.query_params.get('pagina', 1))
            size = int(request.query_params.get('tamano', self.page_size))
        except (ValueError, TypeError):
            raise ValidationError('pagina y tamano deben ser enteros.')
        if not 1 <= page <= 100000 or not 1 <= size <= 500:
            raise ValidationError('pagina: 1..100000; tamano: 1..500.')
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response({'pagina': self.page.number, 'tamano': self.page.paginator.per_page,
                         'total': self.page.paginator.count, 'datos': data})
