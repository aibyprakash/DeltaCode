from django.test import TestCase
from rest_framework.test import APIRequestFactory

from core import models, views


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tenant_a = models.Tenant.objects.create(company_name='A', owner_name='A', email='a@example.com', phone='1', subdomain='a')
        self.tenant_b = models.Tenant.objects.create(company_name='B', owner_name='B', email='b@example.com', phone='2', subdomain='b')
        self.property = models.Property.objects.create(tenant=self.tenant_a, name='PropA', code='P1', address='addr', city='c', state='s', country='x')

    def test_queryset_scoped_by_tenant(self):
        user = models.User.objects.create_user(username='owner', password='pw', tenant=self.tenant_a, role=models.User.Roles.OWNER)
        request = self.factory.get('/api/properties/')
        request.user = user
        request.tenant = self.tenant_a
        view = views.PropertyViewSet()
        view.request = request
        view.queryset = models.Property.objects.all()
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        request.tenant = self.tenant_b
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 0)
