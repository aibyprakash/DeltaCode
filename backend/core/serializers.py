from rest_framework import serializers
from . import models


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tenant
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        exclude = ('password',)


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = '__all__'
        read_only_fields = ('tenant',)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Room
        fields = '__all__'
        read_only_fields = ('tenant',)


class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bed
        fields = '__all__'
        read_only_fields = ('tenant',)


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guest
        fields = '__all__'
        read_only_fields = ('tenant',)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Employee
        fields = '__all__'
        read_only_fields = ('tenant',)


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invoice
        fields = '__all__'
        read_only_fields = ('tenant',)


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentTransaction
        fields = '__all__'
        read_only_fields = ('tenant',)


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Complaint
        fields = '__all__'
        read_only_fields = ('tenant',)


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attendance
        fields = '__all__'
        read_only_fields = ('tenant',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = '__all__'
        read_only_fields = ('tenant',)
