from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from mysite.medium_articles.models import *  # NOQA
from mysite.medium_writers.models import *  # NOQA
