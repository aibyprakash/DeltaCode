from django.test import TestCase

from core import models


class BasicCrudTests(TestCase):
    def setUp(self):
        self.tenant = models.Tenant.objects.create(company_name='Crud', owner_name='Owner', email='c@example.com', phone='1', subdomain='crud')

    def test_create_room(self):
        prop = models.Property.objects.create(tenant=self.tenant, name='Main', code='M1', address='addr', city='c', state='s', country='x')
        room = models.Room.objects.create(tenant=self.tenant, property=prop, room_number='101', room_type=models.Room.RoomTypes.SINGLE, rent_per_bed=5000, max_beds=1)
        self.assertEqual(room.room_number, '101')
        self.assertEqual(room.tenant, self.tenant)
