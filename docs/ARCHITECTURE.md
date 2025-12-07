# PGSaaS Solutions – Multi-tenant PG/Hostel Management

## High-level architecture
- **Frontend**: React Native (Expo) consuming REST APIs via axios. Role-aware navigation for Super Admin, Owner/Manager, Staff, Guest.
- **Backend**: Django + DRF + PostgreSQL. Single database, shared schema with `tenant` foreign key on every domain model. JWT authentication (SimpleJWT). Tenant context resolved from subdomain or `X-Tenant-ID` header via middleware.
- **API Gateway / Reverse Proxy**: Nginx routing `*.pgsystem.com` to Django Gunicorn. Static/media served from object storage (S3-compatible) via CDN when available.
- **Background tasks**: Celery/Redis (future) for notifications, invoice reminders.

## Multi-tenancy pattern
- **Pattern**: Single DB, shared schema, mandatory `tenant` FK on all business tables for logical isolation.
- **Tenant resolution**: Subdomain (e.g., `owner1.pgsystem.com`) or `X-Tenant-ID` header / JWT claim. Middleware sets `request.tenant`. DRF filter backend ensures scoping.
- **Super admin**: Unscoped access. Tenant admins and staff filtered by tenant automatically.

## SaaS context
- Company name: **PGSaaS Solutions**. Subscription tiers: Basic (≤50 beds), Standard (≤200 beds), Premium (unlimited + priority support).
- Onboarding: create Tenant, issue subdomain, invite Owner user, optional CSV import for properties/rooms/beds/guests.
- Support dashboards: Super Admin views tenant health, subscription usage, error logs, payment status.

## Deployment sketch
- **App server**: Gunicorn + Nginx. Environment variables for DB creds, JWT secret, ALLOWED_HOSTS, CORS.
- **DB migrations**: Standard Django migrations; every model carries `tenant` FK to avoid schema per tenant overhead. Preflight data seeding for roles and plans.
- **Media**: S3 bucket with presigned upload from mobile app for KYC IDs.
- **CI/CD**: Run `pytest`, `flake8`, `mypy` (optional), `npm test`. Blue/green deploy or rolling on Kubernetes/containers.

## Authentication flow
1. Client posts credentials to `/api/auth/login/` with `X-Tenant-ID` or via tenant subdomain.
2. SimpleJWT issues access/refresh tokens carrying `tenant` claim (extend token serializer in production).
3. Subsequent requests attach `Authorization: Bearer <token>` and `X-Tenant-ID`; middleware sets `request.tenant` and DRF filters scope data.

## API surface (examples)
- Auth: `/api/auth/login/`, `/api/auth/refresh/`
- Tenants (super admin): `/api/tenants/`
- Properties/Rooms/Beds: `/api/properties/`, `/api/rooms/`, `/api/beds/`
- People: `/api/guests/`, `/api/employees/`
- Finance: `/api/invoices/`, `/api/payments/`
- Ops: `/api/complaints/`, `/api/attendance/`, `/api/notifications/`
- Dashboard: `/api/dashboard/owner-summary/`

## Example cURL
```bash
curl -X POST https://acme.pgsystem.com/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-ID: <tenant_uuid>' \
  -d '{"username": "owner@acme.com", "password": "secret"}'
```

```bash
curl -H 'Authorization: Bearer <token>' -H 'X-Tenant-ID: <tenant_uuid>' \
  https://acme.pgsystem.com/api/properties/
```

```bash
curl -X POST -H 'Authorization: Bearer <token>' -H 'X-Tenant-ID: <tenant_uuid>' \
  -H 'Content-Type: application/json' \
  -d '{"room": 1, "bed": 2, "guest": 3, "amount": "5500.00", "mode": "UPI", "transaction_id": "utr-123"}' \
  https://acme.pgsystem.com/api/payments/
```

## Dashboard KPIs
- Occupancy %, total guests, due amount, active complaints, room/bed counts.

## Future extensions
- Payment gateway integration (UPI deep links), WhatsApp/SMS notifications, IoT access control, staff rostering with Geo check-ins.
