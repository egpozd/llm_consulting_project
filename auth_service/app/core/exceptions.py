class AppError(Exception):
    default_message = "Application error"

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class UserAlreadyExistsError(AppError):
    default_message = "User already exists"


class InvalidCredentialsError(AppError):
    default_message = "Invalid email or password"


class UserNotFoundError(AppError):
    default_message = "User not found"


class InvalidTokenError(AppError):
    default_message = "Invalid token"


class TokenExpiredError(AppError):
    default_message = "Token expired"