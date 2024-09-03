"""add term frequency per corpus view

Revision ID: bd76da865c4e
Revises: 866bca1d8443
Create Date: 2024-08-08 07:16:02.153104

"""

from typing import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bd76da865c4e"
down_revision: Union[str, None] = "866bca1d8443"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    create materialized view term_occurrence_per_corpus_mv as
    select word, ndoc as number_of_articles, nentry as number_of_occurrences
    from ts_stat('select article_content_simple_with_no_stop_words from fastapi_article')
    """
    )
    op.execute(
        """
    create unique index term_occurrence_per_corpus_mv_idx on term_occurrence_per_corpus_mv (word)
    """
    )


def downgrade() -> None:
    op.execute("drop materialized view term_occurrence_per_corpus_mv")
