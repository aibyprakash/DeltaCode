from rest_framework import filters


class TenantFilterBackend(filters.BaseFilterBackend):
    """Ensure querysets are filtered by tenant derived from request."""

    def filter_queryset(self, request, queryset, view):
        tenant = getattr(request, 'tenant', None)
        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_superuser', False):
            return queryset
        if tenant:
            return queryset.filter(tenant=tenant)
        if user and hasattr(user, 'tenant') and user.tenant:
            return queryset.filter(tenant=user.tenant)
        return queryset.none()
