"""add precalculated tsvector

Revision ID: 866bca1d8443
Revises: fd88ac4beb88
Create Date: 2024-08-06 13:32:23.180959

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "866bca1d8443"
down_revision: Union[str, None] = "fd88ac4beb88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "fastapi_article",
        sa.Column(
            "article_content_simple_with_no_stop_words",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('simple_with_stop_words', article_content)", persisted=True),
            nullable=True,
        ),
    )
    op.create_index(
        "article_content_simple_with_no_stop_words_idx",
        "fastapi_article",
        ["article_content_simple_with_no_stop_words"],
        unique=False,
        postgresql_using="gin",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("article_content_simple_with_no_stop_words_idx", table_name="fastapi_article", postgresql_using="gin")
    op.drop_column("fastapi_article", "article_content_simple_with_no_stop_words")
    # ### end Alembic commands ###