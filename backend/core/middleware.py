from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseBadRequest

from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    header_name = 'HTTP_X_TENANT_ID'

    def process_request(self, request):
        tenant_id = request.META.get(self.header_name)
        if not tenant_id:
            host = request.get_host().split(':')[0]
            parts = host.split('.')
            if len(parts) > 2:
                tenant_subdomain = parts[0]
                tenant = Tenant.objects.filter(subdomain=tenant_subdomain).first()
                if tenant:
                    request.tenant = tenant
                    return None
        if tenant_id:
            try:
                request.tenant = Tenant.objects.get(id=tenant_id)
                return None
            except Tenant.DoesNotExist:
                return HttpResponseBadRequest('Invalid tenant header provided')
        request.tenant = None
        return None
