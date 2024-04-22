from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mysite import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": "-c timezone=utc"},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as error:
        db.rollback()
        raise error
    finally:
        db.close()
