from django.http import JsonResponse
from django.views.decorators.http import require_safe

@require_safe
def healthz(request):
    # Process liveness only. Database readiness remains protected at /api/health/.
    return JsonResponse({'estado': 'activo'})
