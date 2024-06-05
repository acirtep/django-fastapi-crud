from sqlalchemy import UUID
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import literal
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from mysite.articles.constants import ArticleStatus
from mysite.models import Base


class Article(Base):

    __tablename__ = "fastapi_article"
    __table_args__ = {"comment": "general information about articles"}

    article_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text(
            "gen_random_uuid()",
        ),
        comment="unique identifier of the article",
    )

    article_name = Column(String, nullable=False, comment="the content of the article")
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
