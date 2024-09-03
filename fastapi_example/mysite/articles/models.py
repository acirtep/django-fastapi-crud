from sqlalchemy import UUID
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Computed
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import literal
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from mysite.articles.constants import ArticleStatus
from mysite.models import Base


class ArticleTags(Base):
    __tablename__ = "fastapi_article_tags"
    __table_args__ = {"comment": "association table between article and tag"}

    article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fastapi_article.article_id", ondelete="CASCADE"),
        comment="the id of the article",
        primary_key=True,
    )

    tag_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fastapi_tag.tag_id", ondelete="CASCADE"),
        comment="the id of the tag",
        primary_key=True,
    )


class Tag(Base):

    __tablename__ = "fastapi_tag"
    __table_args__ = {"comment": "general information about article tags"}

    tag_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text(
            "gen_random_uuid()",
        ),
        comment="unique identifier of the tag",
    )

    tag_name = Column(String(length=70), nullable=False, unique=True, comment="the name of the tag")

    date_created = Column(
        DateTime(timezone=True),
        server_default=text("statement_timestamp()"),
        nullable=False,
        comment="the date time in UTC, when the tag was created",
    )

    articles = relationship("Article", secondary="fastapi_article_tags", back_populates="tags", passive_deletes=True)
    article_name = association_proxy(target_collection="articles", attr="article_name")


class Article(Base):

    __tablename__ = "fastapi_article"
    __table_args__ = (
        Index(
            "article_content_simple_with_no_stop_words_idx",
            "article_content_simple_with_no_stop_words",
            postgresql_using="gin",
        ),
        {"comment": "general information about articles"},
    )

    article_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text(
            "gen_random_uuid()",
        ),
        comment="unique identifier of the article",
    )

    article_name = Column(String, nullable=False, comment="the name of the article")
    article_content = Column(Text, nullable=True, comment="the content of the article")

    date_created = Column(
        DateTime(timezone=True),
        server_default=text("statement_timestamp()"),
        nullable=False,
        comment="the date time in UTC, when the article was created",
    )

    date_updated = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="the date time in UTC, when the article was update",
    )

    date_first_published = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="the date time in UTC, when the article was published the first time",
    )

    article_status = Column(
        String,
        server_default=literal(ArticleStatus.draft.value),
        nullable=False,
        comment="the status of the article",
    )

    members_only_flag = Column(
        Boolean, server_default=expression.false(), nullable=False, comment="true if it is a members only article"
    )

    writer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fastapi_writer.writer_id", ondelete="CASCADE"),
        comment="the writer of the article",
        index=True,
    )

    writer = relationship("Writer", passive_deletes=True, back_populates="articles")

    tags = relationship("Tag", secondary="fastapi_article_tags", back_populates="articles", passive_deletes=True)

    # tag_bulk_upload = relationship("Tag", secondary="fastapi_article_tags", lazy="write_only", passive_deletes=True)

    article_content_simple_with_no_stop_words = Column(
        TSVECTOR, Computed("to_tsvector('simple_with_stop_words', article_content)", persisted=True)
    )
