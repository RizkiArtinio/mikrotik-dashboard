import os

from cryptography.fernet import Fernet

# Must be set before any `app.*` module is imported, since app.core.config
# reads the environment once at import time.
os.environ.setdefault("FERNET_KEY", Fernet.generate_key().decode())
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
