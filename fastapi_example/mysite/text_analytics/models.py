from sqlalchemy import UUID
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from mysite.models import Base


class CorpusTermOccurrenceMV(Base):
    __tablename__ = "term_occurrence_per_corpus_mv"
    __table_args__ = {"info": {"is_view": True, "skip_autogenerate": True}}

    word = Column(String, nullable=False, primary_key=True)

    number_of_articles = Column(Integer, nullable=False)

    number_of_occurrences = Column(Integer, nullable=False)


class ArticleTermOccurrenceMV(Base):
    __tablename__ = "term_occurrence_per_article_mv"
    __table_args__ = {"info": {"is_view": True, "skip_autogenerate": True}}

    article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fastapi_article.article_id"),  # information only
        primary_key=True,
    )

    word = Column(String, nullable=False, primary_key=True)

    number_of_occurrences = Column(Integer, nullable=False)
