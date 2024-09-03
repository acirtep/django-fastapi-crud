"""add term frequency per article view

Revision ID: 423ee5dc11d9
Revises: bd76da865c4e
Create Date: 2024-08-08 07:27:12.057713

"""

from typing import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "423ee5dc11d9"
down_revision: Union[str, None] = "bd76da865c4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    create materialized view term_occurrence_per_article_mv as
    select
        article_id,
        word,
        nentry as number_of_occurrences
    from fastapi_article,
        ts_stat('select article_content_simple_with_no_stop_words from fastapi_article where article_id = ' || '''' ||
                      fastapi_article.article_id || '''' || '::uuid')
    """
    )

    op.execute(
        """
    create unique index term_occurrence_per_article_mv_idx on term_occurrence_per_article_mv (article_id, word)
    """
    )


def downgrade() -> None:
    op.execute("drop materialized view term_occurrence_per_article_mv")
