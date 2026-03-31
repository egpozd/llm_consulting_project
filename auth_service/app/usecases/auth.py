from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def register(self, data: RegisterRequest) -> UserPublic:
        existing_user = await self.users_repo.get_by_email(data.email)
        if existing_user is not None:
            raise UserAlreadyExistsError()

        password_hash = hash_password(data.password)
        user = await self.users_repo.create(
            email=data.email,
            password_hash=password_hash,
            role="user",
        )
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.users_repo.get_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        token = create_access_token(user_id=user.id, role=user.role)
        return TokenResponse(access_token=token)

    async def me(self, user_id: int) -> UserPublic:
        user = await self.users_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        return UserPublic.model_validate(user)