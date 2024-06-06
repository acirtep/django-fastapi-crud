"""articles

Revision ID: f0aba27820ec
Revises: ab1bfe48ad14
Create Date: 2024-06-05 19:57:51.216696

"""

from typing import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f0aba27820ec"
down_revision: Union[str, None] = "ab1bfe48ad14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "fastapi_article",
        sa.Column(
            "article_id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="unique identifier of the article",
        ),
        sa.Column("article_name", sa.String(), nullable=False, comment="the content of the article"),
        sa.Column("article_content", sa.Text(), nullable=True, comment="the content of the article"),
        sa.Column(
            "date_created",
            sa.DateTime(timezone=True),
            server_default=sa.text("statement_timestamp()"),
            nullable=False,
            comment="the date time in UTC, when the article was created",
        ),
        sa.Column(
            "date_updated",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="the date time in UTC, when the article was update",
        ),
        sa.Column(
            "date_first_published",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="the date time in UTC, when the article was published the first time",
        ),
        sa.Column(
            "article_status",
            sa.String(),
            server_default=sa.text("'DRAFT'"),
            nullable=False,
            comment="the status of the article",
        ),
        sa.Column(
            "members_only_flag",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment="true if it is a members only article",
        ),
        sa.Column("writer_id", sa.UUID(), nullable=True, comment="the writer of the article"),
        sa.ForeignKeyConstraint(["writer_id"], ["fastapi_writer.writer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("article_id"),
        comment="general information about articles",
    )
    op.create_index(op.f("ix_fastapi_article_article_id"), "fastapi_article", ["article_id"], unique=False)
    op.create_index(op.f("ix_fastapi_article_writer_id"), "fastapi_article", ["writer_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_fastapi_article_writer_id"), table_name="fastapi_article")
    op.drop_index(op.f("ix_fastapi_article_article_id"), table_name="fastapi_article")
    op.drop_table("fastapi_article")
    # ### end Alembic commands ###
