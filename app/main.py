from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import AppException
from app.database import SessionLocal
from app.routers import (
    admin,
    auth,
    bookings_admin,
    bookings_student,
    notifications,
    payments_admin,
    payments_student,
    reports,
    seats,
    seats_public,
)
from app.services import scheduler_service

app = FastAPI(title=settings.PROJECT_NAME)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error", "data": None},
    )


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(seats.router)
app.include_router(seats_public.router)
app.include_router(bookings_admin.router)
app.include_router(bookings_student.router)
app.include_router(payments_admin.router)
app.include_router(payments_student.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(notifications.admin_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}


@app.on_event("startup")
def seed_initial_admin():
    from app.core.enums import RoleEnum, UserStatusEnum
    from app.models.user import User
    from app.services.security import generate_user_id, hash_password

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()

        if existing:
            # Self-heal: if a previous run failed mid-way and left this admin
            # without login credentials, complete the seeding now.
            if not existing.user_id or not existing.hashed_password:
                existing.user_id = existing.user_id or generate_user_id(existing.id)
                existing.hashed_password = hash_password(settings.ADMIN_PASSWORD)
                existing.role = RoleEnum.admin
                existing.status = UserStatusEnum.active
                db.commit()
                print(
                    "Repaired incomplete admin record -> "
                    f"User ID: {existing.user_id} | Password: {settings.ADMIN_PASSWORD}"
                )
            return

        # Build the full record (including credentials) before the first
        # commit, so no half-seeded row is ever persisted.
        admin_user = User(
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL,
            role=RoleEnum.admin,
            status=UserStatusEnum.active,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
        )
        db.add(admin_user)
        db.flush()  # assigns admin_user.id without committing

        admin_user.user_id = generate_user_id(admin_user.id)
        db.commit()

        print(
            "Seeded initial admin -> "
            f"User ID: {admin_user.user_id} | Password: {settings.ADMIN_PASSWORD}"
        )
    finally:
        db.close()


@app.on_event("startup")
def start_scheduler():
    scheduler_service.start()


@app.on_event("shutdown")
def stop_scheduler():
    scheduler_service.shutdown()
