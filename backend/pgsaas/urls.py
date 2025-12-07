from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core import views as core_views

router = routers.DefaultRouter()
router.register(r'tenants', core_views.TenantViewSet, basename='tenant')
router.register(r'properties', core_views.PropertyViewSet, basename='property')
router.register(r'rooms', core_views.RoomViewSet, basename='room')
router.register(r'beds', core_views.BedViewSet, basename='bed')
router.register(r'guests', core_views.GuestViewSet, basename='guest')
router.register(r'employees', core_views.EmployeeViewSet, basename='employee')
router.register(r'invoices', core_views.InvoiceViewSet, basename='invoice')
router.register(r'payments', core_views.PaymentTransactionViewSet, basename='payment')
router.register(r'complaints', core_views.ComplaintViewSet, basename='complaint')
router.register(r'attendance', core_views.AttendanceViewSet, basename='attendance')
router.register(r'notifications', core_views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/dashboard/owner-summary/', core_views.OwnerDashboardView.as_view(), name='owner-dashboard'),
    path('api/', include(router.urls)),
]
