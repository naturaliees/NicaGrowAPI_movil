from decimal import Decimal
from rest_framework.renderers import JSONRenderer

def exact_decimals(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {k: exact_decimals(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [exact_decimals(v) for v in value]
    return value

class ExactJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super().render(exact_decimals(data), accepted_media_type, renderer_context)
