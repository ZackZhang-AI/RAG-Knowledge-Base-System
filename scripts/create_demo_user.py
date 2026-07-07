import os

from src.database.models import User
from src.database.sql_session import Base, SessionLocal, engine
from src.utils.security import get_password_hash


def main() -> None:
    username = os.getenv("DEMO_USERNAME", "demo")
    email = os.getenv("DEMO_EMAIL", "demo@example.com")
    password = os.getenv("DEMO_PASSWORD")

    if not password:
        raise RuntimeError("Set DEMO_PASSWORD before creating the demo user.")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.email = email
            user.password_hash = get_password_hash(password)
            user.is_active = True
            print(f"Updated demo user: {username}")
        else:
            db.add(
                User(
                    username=username,
                    email=email,
                    password_hash=get_password_hash(password),
                    is_active=True,
                )
            )
            print(f"Created demo user: {username}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
