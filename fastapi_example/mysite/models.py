from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from mysite.articles.models import *  # NOQA
from mysite.writers.models import *  # NOQA
