from app.db import Base, engine
from app.models import *  # noqa: F403


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database schema created")


if __name__ == "__main__":
    main()
