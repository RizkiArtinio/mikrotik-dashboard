from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User


class AuthError(Exception):
    pass


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user


def issue_token(user: User) -> str:
    return create_access_token(subject=user.email, role=user.role.value)


async def create_user(db: AsyncSession, *, email: str, password: str, full_name: str | None, role) -> User:
    user = User(email=email, full_name=full_name, hashed_password=hash_password(password), role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
