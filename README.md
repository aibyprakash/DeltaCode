# PGSaaS Solutions – Multi-tenant PG/Hostel Management (Starter)

This repository provides a technical starter kit and blueprint for a multi-tenant Paying Guest/Hostel Management SaaS built with Django/DRF + PostgreSQL and a React Native mobile app.

## Contents
- `docs/ARCHITECTURE.md` – architecture, multi-tenancy pattern, deployment guidance, example cURL.
- `backend/` – Django project skeleton with multi-tenant models, middleware, DRF viewsets, and sample tests.
- `frontend/` – React Native (Expo-ready) starter with auth context, dashboard, and room listing screens.

## Running locally (outline)
1. Create and activate a virtualenv, then install `backend/requirements.txt`.
2. Export `DJANGO_SETTINGS_MODULE=pgsaas.settings` and run `python manage.py migrate` inside `backend/` once PostgreSQL is available.
3. Start the API: `python manage.py runserver 0.0.0.0:8000`.
4. For the app, install dependencies (`npm install` / `yarn`) and run `npx expo start` from `frontend/`.

## Multi-tenancy choices
- Single database, shared schema; every domain model carries a `tenant` foreign key.
- Tenant resolution through subdomain or `X-Tenant-ID` header, enforced via middleware and DRF filter backend.

## Notes
- JWT authentication via SimpleJWT is wired in settings and URLs; extend token claims for tenant/role in production.
- Tests in `backend/core/tests` illustrate tenant isolation, permissions, and basic CRUD.
