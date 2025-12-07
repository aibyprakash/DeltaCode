from django.db.models import Count, Sum
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response

from . import models, serializers, permissions as core_permissions


class TenantScopedModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        base_qs = self.queryset
        request = self.request
        if request.user.is_superuser or request.user.role == request.user.Roles.SUPER_ADMIN:
            return base_qs
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'tenant', None)
        return base_qs.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'tenant', None)
        serializer.save(tenant=tenant)


class TenantViewSet(TenantScopedModelViewSet):
    queryset = models.Tenant.objects.all()
    serializer_class = serializers.TenantSerializer
    permission_classes = [core_permissions.IsSuperAdmin]


class PropertyViewSet(TenantScopedModelViewSet):
    queryset = models.Property.objects.all()
    serializer_class = serializers.PropertySerializer
    permission_classes = [permissions.IsAuthenticated, core_permissions.IsOwnerOrManager]


class RoomViewSet(TenantScopedModelViewSet):
    queryset = models.Room.objects.select_related('property').all()
    serializer_class = serializers.RoomSerializer
    permission_classes = [permissions.IsAuthenticated, core_permissions.IsOwnerOrManager]


class BedViewSet(TenantScopedModelViewSet):
    queryset = models.Bed.objects.select_related('room').all()
    serializer_class = serializers.BedSerializer
    permission_classes = [permissions.IsAuthenticated, core_permissions.IsOwnerOrManager]


class GuestViewSet(TenantScopedModelViewSet):
    queryset = models.Guest.objects.select_related('user').all()
    serializer_class = serializers.GuestSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmployeeViewSet(TenantScopedModelViewSet):
    queryset = models.Employee.objects.select_related('user').all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, core_permissions.IsOwnerOrManager]


class InvoiceViewSet(TenantScopedModelViewSet):
    queryset = models.Invoice.objects.select_related('guest', 'room', 'bed').all()
    serializer_class = serializers.InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentTransactionViewSet(TenantScopedModelViewSet):
    queryset = models.PaymentTransaction.objects.select_related('invoice').all()
    serializer_class = serializers.PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ComplaintViewSet(TenantScopedModelViewSet):
    queryset = models.Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]


class AttendanceViewSet(TenantScopedModelViewSet):
    queryset = models.Attendance.objects.select_related('employee').all()
    serializer_class = serializers.AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationViewSet(TenantScopedModelViewSet):
    queryset = models.Notification.objects.select_related('user').all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class OwnerDashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'tenant', None)
        rooms = models.Room.objects.filter(tenant=tenant).count()
        occupied_beds = models.Bed.objects.filter(tenant=tenant, status=models.Bed.Status.OCCUPIED).count()
        total_beds = models.Bed.objects.filter(tenant=tenant).count()
        occupancy = round((occupied_beds / total_beds) * 100, 2) if total_beds else 0
        total_due = models.Invoice.objects.filter(tenant=tenant, status=models.Invoice.Status.PENDING).aggregate(
            amount=Sum('amount')
        )['amount'] or 0
        active_complaints = models.Complaint.objects.filter(tenant=tenant, status=models.Complaint.Status.OPEN).count()
        guests = models.Guest.objects.filter(tenant=tenant).count()

        return Response(
            {
                'occupancy_percent': occupancy,
                'total_guests': guests,
                'total_due_amount': total_due,
                'active_complaints': active_complaints,
                'total_rooms': rooms,
                'total_beds': total_beds,
            }
        )
