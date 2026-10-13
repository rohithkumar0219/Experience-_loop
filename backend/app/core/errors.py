from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, message: str, detail: str = None):
        super().__init__(
            status_code=status_code,
            detail={"message": message, "error_detail": detail or message}
        )


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str = None):
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} with id '{identifier}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=msg)


class BadRequestError(AppError):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message)
