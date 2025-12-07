from django.test import TestCase
from rest_framework.test import APIRequestFactory

from core import models, views


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tenant = models.Tenant.objects.create(company_name='T', owner_name='O', email='o@example.com', phone='1', subdomain='t')

    def test_super_admin_can_list_tenants(self):
        user = models.User.objects.create_user(username='super', password='pw', role=models.User.Roles.SUPER_ADMIN)
        request = self.factory.get('/api/tenants/')
        request.user = user
        view = views.TenantViewSet()
        view.request = request
        view.queryset = models.Tenant.objects.all()
        self.assertTrue(view.check_permissions(request) is None)

    def test_staff_cannot_list_tenants(self):
        user = models.User.objects.create_user(username='staff', password='pw', tenant=self.tenant, role=models.User.Roles.STAFF)
        request = self.factory.get('/api/tenants/')
        request.user = user
        view = views.TenantViewSet()
        view.request = request
        view.queryset = models.Tenant.objects.all()
        with self.assertRaises(Exception):
            view.check_permissions(request)
