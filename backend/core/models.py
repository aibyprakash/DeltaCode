from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    company_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    subscription_plan = models.CharField(max_length=50, default='basic')
    subdomain = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class User(AbstractUser):
    class Roles(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        OWNER = 'OWNER', 'Owner'
        MANAGER = 'MANAGER', 'Manager'
        STAFF = 'STAFF', 'Staff'
        TENANT = 'TENANT', 'Tenant'

    tenant = models.ForeignKey(Tenant, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STAFF)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def is_tenant_admin(self):
        return self.role in {self.Roles.OWNER, self.Roles.MANAGER}


class BaseTenantModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Property(BaseTenantModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    total_rooms = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('tenant', 'code')

    def __str__(self):
        return f"{self.name} ({self.code})"


class Room(BaseTenantModel):
    class RoomTypes(models.TextChoices):
        SINGLE = 'SINGLE', 'Single'
        DOUBLE = 'DOUBLE', 'Double'
        DORM = 'DORM', 'Dormitory'

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    room_type = models.CharField(max_length=20, choices=RoomTypes.choices)
    rent_per_bed = models.DecimalField(max_digits=10, decimal_places=2)
    max_beds = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tenant', 'property', 'room_number')

    def __str__(self):
        return f"Room {self.room_number}"


class Bed(BaseTenantModel):
    class Status(models.TextChoices):
        VACANT = 'VACANT', 'Vacant'
        OCCUPIED = 'OCCUPIED', 'Occupied'
        BLOCKED = 'BLOCKED', 'Blocked'

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VACANT)

    class Meta:
        unique_together = ('tenant', 'room', 'bed_number')

    def __str__(self):
        return f"Bed {self.bed_number} - {self.status}"


class Guest(BaseTenantModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guest_profile')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    id_proof = models.CharField(max_length=50, blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    check_in = models.DateField(default=timezone.now)
    planned_check_out = models.DateField(null=True, blank=True)
    current_bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True)


class Employee(BaseTenantModel):
    class Roles(models.TextChoices):
        MANAGER = 'MANAGER', 'Manager'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
        HOUSEKEEPING = 'HOUSEKEEPING', 'Housekeeping'
        SECURITY = 'SECURITY', 'Security'
        COOK = 'COOK', 'Cook'

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    role = models.CharField(max_length=30, choices=Roles.choices)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shift_timing = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, default='ACTIVE')


class Invoice(BaseTenantModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('tenant', 'invoice_number')


class PaymentTransaction(BaseTenantModel):
    class Mode(models.TextChoices):
        CASH = 'CASH', 'Cash'
        UPI = 'UPI', 'UPI'
        CARD = 'CARD', 'Card'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=20, choices=Mode.choices)
    transaction_id = models.CharField(max_length=100)
    transaction_date = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True)


class Complaint(BaseTenantModel):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    guest = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to = models.ForeignKey(Employee, related_name='assigned_complaints', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Attendance(BaseTenantModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_logs')
    date = models.DateField(default=timezone.now)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)


class Notification(BaseTenantModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
