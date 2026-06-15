# Library Seat Booking System — Phase 1, 2, 3, 4 & 5

Phase 1 delivers: project setup, configuration, database models, and the
authentication foundation (registration, admin approval, credential email,
login, JWT, role-based access).

Phase 2 adds: seat management (CRUD), extended student management
(update/delete/status), and an available-seats endpoint for students.

Phase 3 adds: booking management — students can book/cancel seats for
themselves, admins have full booking CRUD, seat availability is now
booking-aware, and overdue bookings auto-expire.

Phase 4 adds: payments (per-seat pricing, manual recording by staff),
dues tracking, admin reports (occupancy/revenue/students/bookings), and a
daily scheduled job for expiry/overdue checks and reminder emails.

Phase 5 adds: an in-app notification system — every account, booking, and
payment event from Phases 1-4 now also creates a notification record
(`/api/v1/notifications`), in addition to its existing email. This gives a
frontend everything it needs for a notification bell/dropdown (unread count,
list, mark as read), and lets admins broadcast custom messages.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # then edit .env (SECRET_KEY, SMTP, admin creds)
```

## Database

Tables are managed via Alembic migrations (no auto-create on startup):

```bash
alembic upgrade head
```

Run this once before starting the server, and again after any future model
changes (after generating a new migration with `alembic revision --autogenerate -m "..."`).

## Run the server

```bash
uvicorn app.main:app --reload
```

On startup, an initial admin account is seeded using `ADMIN_EMAIL` /
`ADMIN_PASSWORD` from `.env`. The generated login `user_id` (e.g.
`LIB-2026-0001`) is printed to the console on first run — use it to log in.

To create additional admins (or re-create one manually), run:

```bash
python -m scripts.create_admin --name "Jane Admin" --email jane@library.com --password Secret123
```

API docs: http://127.0.0.1:8000/docs

## Endpoints (Phase 1)

### Auth
| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/auth/register` | Public — student self-registration (status: pending) |
| POST | `/api/v1/auth/login` | Public — OAuth2 form (`username`=User ID, `password`=Password) |
| POST | `/api/v1/auth/refresh` | Public (valid refresh token) |
| GET  | `/api/v1/auth/me` | Authenticated |

### Admin — User Management
| Method | Path | Access |
|---|---|---|
| GET  | `/api/v1/admin/users/pending` | Admin |
| GET  | `/api/v1/admin/users` | Admin — filter by `role`, `status`, paginated |
| GET  | `/api/v1/admin/users/{id}` | Admin |
| POST | `/api/v1/admin/users` | Admin — create user directly (auto-activated, credentials emailed) |
| POST | `/api/v1/admin/users/{id}/approve` | Admin — approve pending user, generate & email credentials |
| POST | `/api/v1/admin/users/{id}/reject` | Admin — reject pending user |
| PATCH | `/api/v1/admin/users/{id}` | Admin — update profile (full_name, phone) |
| PATCH | `/api/v1/admin/users/{id}/status` | Admin — activate/deactivate a user (active ↔ inactive, or reactivate rejected) |
| DELETE | `/api/v1/admin/users/{id}` | Admin — delete a user (cannot delete self) |

## Endpoints (Phase 2)

### Admin — Seat Management
| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/admin/seats` | Admin — create seat (seat_number is normalized to uppercase; optional `price` for per-seat pricing) |
| GET  | `/api/v1/admin/seats` | Admin — list seats, filter by `status`, `zone`, `floor`, paginated |
| GET  | `/api/v1/admin/seats/{id}` | Admin — get seat details |
| PATCH | `/api/v1/admin/seats/{id}` | Admin — update seat (any field, including status, price) |
| DELETE | `/api/v1/admin/seats/{id}` | Admin — delete seat |

### Seats (Student/Admin)
| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/seats/available` | Authenticated — list seats with `status=available`, paginated |

## Endpoints (Phase 3)

### Admin — Booking Management
| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/admin/bookings` | Admin — create booking for any student (`student_id`, `seat_id`, `start_date`, `duration_months` or `end_date`, `notes`) |
| GET  | `/api/v1/admin/bookings` | Admin — list all bookings, filter by `student_id`, `seat_id`, `status`, paginated |
| GET  | `/api/v1/admin/bookings/{id}` | Admin — get booking details |
| PATCH | `/api/v1/admin/bookings/{id}` | Admin — full update (dates, status, notes) |
| POST | `/api/v1/admin/bookings/{id}/cancel` | Admin — cancel any booking |
| DELETE | `/api/v1/admin/bookings/{id}` | Admin — hard delete a booking (corrections only) |

### Bookings (Student)
| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/bookings` | Authenticated student — book an available seat for self (`seat_id`, optional `start_date`, `duration_months` default 1) |
| GET | `/api/v1/bookings/me` | Authenticated — list own booking history, paginated |
| GET | `/api/v1/bookings/me/active` | Authenticated — get current active booking, or `null` if none |
| POST | `/api/v1/bookings/{id}/cancel` | Authenticated — cancel own active booking |

## Endpoints (Phase 4)

### Admin — Payment Management
| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/admin/payments` | Admin — list all payments, filter by `student_id`, `status`, paginated |
| POST | `/api/v1/admin/payments` | Admin — create manual/ad-hoc payment (`student_id`, `amount`, `due_date`, optional `booking_id`, `notes`) |
| GET | `/api/v1/admin/payments/students/{student_id}/dues` | Admin — get a student's dues summary |
| GET | `/api/v1/admin/payments/{id}` | Admin — get payment details |
| PATCH | `/api/v1/admin/payments/{id}` | Admin — update amount/due_date/notes (only while `pending`/`overdue`) |
| POST | `/api/v1/admin/payments/{id}/mark-paid` | Admin — mark as paid (`method`, optional `transaction_ref`, `notes`, `paid_at`); sends confirmation email |
| POST | `/api/v1/admin/payments/{id}/waive` | Admin — waive a payment (requires `notes`) |
| POST | `/api/v1/admin/payments/{id}/refund` | Admin — mark a paid payment as refunded (requires `notes`) |

### Payments (Student)
| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/payments/me` | Authenticated — list own payment history, paginated |
| GET | `/api/v1/payments/me/dues` | Authenticated — get own outstanding dues summary |

### Admin — Reports
| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/admin/reports/occupancy` | Admin — seat occupancy stats (total, available, occupied, maintenance, inactive, occupancy %) |
| GET | `/api/v1/admin/reports/revenue` | Admin — revenue summary; query params `start_date`, `end_date` (filters by payment `due_date`) |
| GET | `/api/v1/admin/reports/students` | Admin — student growth/status stats; query params `start_date`, `end_date` |
| GET | `/api/v1/admin/reports/bookings` | Admin — booking stats (active, expired, cancelled, expiring soon, cancellation rate) |

## Endpoints (Phase 5)

### Notifications (Authenticated)
| Method | Path | Access |
|---|---|---|
| GET | `/api/v1/notifications` | Authenticated — list own notifications, paginated; optional `is_read` filter; response includes `unread_count` |
| GET | `/api/v1/notifications/unread-count` | Authenticated — lightweight count for a bell badge |
| POST | `/api/v1/notifications/mark-read` | Authenticated — mark specific `notification_ids` as read, or all if omitted |
| POST | `/api/v1/notifications/{id}/mark-read` | Authenticated — mark a single notification as read |

### Admin — Notifications
| Method | Path | Access |
|---|---|---|
| POST | `/api/v1/admin/notifications/broadcast` | Admin — send a custom notification; `target`: `all_students`, `all_admins`, or `specific_user` (with `user_id`) |

## Email

If SMTP settings are not configured in `.env`, emails are logged to the
console instead of being sent — useful for local development.

## Notes

- SQLite is used now (`DATABASE_URL=sqlite:///./library.db`); swapping to
  PostgreSQL/MySQL later only requires changing `DATABASE_URL` and the
  SQLAlchemy driver, plus reviewing the Alembic migration for enum types.
- `User` is a single unified table with `role` and `status` enums to support
  future roles (e.g. `staff`) and lifecycle states without schema changes.
- Soft status flags (`status`) are used instead of hard deletes for audit
  trail purposes going forward.
- `Seat.status` includes `available`, `occupied`, `maintenance`, `inactive`.
  Seat deletion and status changes to `maintenance`/`inactive` are now
  blocked if the seat has an active booking (Phase 3).
- `PATCH /api/v1/admin/users/{id}/status` only allows manual transitions
  between `active` and `inactive`, or reactivating a `rejected` user who was
  previously approved. The `pending` → `active`/`rejected` flow stays on the
  dedicated approve/reject endpoints. Admins cannot change their own status
  or delete their own account via these endpoints.
- **Booking rules**: a student can hold only one `active` booking at a time;
  a seat can have only one `active` booking at a time. Booking duration
  defaults to 1 month (max 12) via `duration_months`, or admins may set an
  explicit `end_date`. `Booking.status`: `active`, `expired`, `cancelled`,
  `completed`.
- **Lazy expiry**: in addition to the daily scheduler (below), bookings with
  `end_date < today` and payments with `due_date < today` are also checked
  and updated whenever a relevant booking/payment endpoint is called — a
  safety net in case the scheduler misses a run. Both mechanisms are
  idempotent and safe to run together.
- A booking confirmation email is sent on successful booking (student
  self-booking or admin-created).
- **Pricing**: each `Seat` has an optional `price` (monthly). If not set,
  `DEFAULT_MONTHLY_SEAT_FEE` from `.env` is used. Creating a booking
  automatically creates a `pending` Payment with `due_date = booking.start_date
  + PAYMENT_DUE_GRACE_DAYS`.
- **Payments**: recorded manually by admin/staff (cash, UPI, card, bank
  transfer) — no online payment gateway integration. `Payment.status`:
  `pending`, `paid`, `overdue`, `waived`, `refunded`. Waiving/refunding
  require a `notes` field for audit trail. A `paid` payment can only move to
  `refunded`; a `waived`/`refunded` payment is terminal.
- **Scheduler**: a daily APScheduler job (time configurable via
  `SCHEDULER_HOUR`/`SCHEDULER_MINUTE`, default 01:00) expires overdue
  bookings, flags overdue payments, and sends reminder emails
  (`REMINDER_DAYS_BEFORE`, default 3 days) for bookings expiring soon and
  payments due soon. Disable via `SCHEDULER_ENABLED=False`.
- **Reports**: all admin report endpoints return aggregated counts/sums via
  SQL — no row-by-row loading. Revenue report filters by payment `due_date`
  range, not `paid_at`.
- **Notifications**: every account/booking/payment event that previously sent
  only an email (Phases 1-4) now also creates an in-app `Notification` record
  via `app/services/notification_service.py`. Email behavior is unchanged —
  notifications are additive. Notification types are listed in
  `NotificationTypeEnum` (`app/core/enums.py`); each has a fixed `title` and
  a generated `message`, plus an optional `link` and
  `related_entity_type`/`related_entity_id` for frontend deep-linking.
  - **Student notifications**: registration submitted, account
    approved/rejected/status-changed, booking confirmed/cancelled/expiring
    soon/expired, payment recorded/due soon/overdue/waived/refunded.
  - **Admin notifications**: new registration, seat booked (student
    self-service), booking cancelled by student.
  - Expiry/overdue notifications are created exactly once, at the moment a
    booking/payment transitions to `expired`/`overdue` (both the lazy check
    and the daily scheduler call the same underlying transition function, so
    there's no duplication).
  - Admins can also send ad-hoc broadcast notifications (`GENERIC` type) to
    all students, all admins, or a specific user.




