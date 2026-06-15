from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception with sensible defaults."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(AppException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class EmailAlreadyExistsException(AppException):
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidCredentialsException(AppException):
    def __init__(self, detail: str = "Invalid user ID or password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UserNotActiveException(AppException):
    def __init__(self, detail: str = "Account is not active yet"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class InvalidStatusTransitionException(AppException):
    def __init__(self, detail: str = "Invalid status transition for this user"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InsufficientPermissionsException(AppException):
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class InvalidTokenException(AppException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class SeatNotFoundException(AppException):
    def __init__(self, detail: str = "Seat not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class SeatAlreadyExistsException(AppException):
    def __init__(self, detail: str = "A seat with this seat number already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class SeatInUseException(AppException):
    def __init__(self, detail: str = "Seat cannot be modified or deleted while in use"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidOperationException(AppException):
    def __init__(self, detail: str = "Invalid operation"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class BookingNotFoundException(AppException):
    def __init__(self, detail: str = "Booking not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class SeatNotAvailableException(AppException):
    def __init__(self, detail: str = "Seat is not available for booking"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class StudentAlreadyHasActiveBookingException(AppException):
    def __init__(self, detail: str = "Student already has an active booking"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class BookingNotActiveException(AppException):
    def __init__(self, detail: str = "Booking is not active"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class BookingAccessDeniedException(AppException):
    def __init__(self, detail: str = "You do not have access to this booking"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class PaymentNotFoundException(AppException):
    def __init__(self, detail: str = "Payment not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PaymentAlreadyPaidException(AppException):
    def __init__(self, detail: str = "Payment has already been marked as paid"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidPaymentStatusTransitionException(AppException):
    def __init__(self, detail: str = "Invalid status transition for this payment"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class PaymentAccessDeniedException(AppException):
    def __init__(self, detail: str = "You do not have access to this payment"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotificationNotFoundException(AppException):
    def __init__(self, detail: str = "Notification not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
