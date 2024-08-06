"""create dictionary

Revision ID: fd88ac4beb88
Revises: 407b70a35999
Create Date: 2024-08-06 12:32:35.869182

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fd88ac4beb88"
down_revision: Union[str, None] = "407b70a35999"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TEXT SEARCH DICTIONARY simple_with_stop_words_dict (
            TEMPLATE = pg_catalog.simple,
            STOPWORDS = english
        )
        """
    )

    op.execute(
        """
        CREATE TEXT SEARCH CONFIGURATION simple_with_stop_words (COPY = simple);
        """
    )

    op.execute(
        """
        ALTER  TEXT SEARCH CONFIGURATION simple_with_stop_words
        ALTER MAPPING FOR asciiword, word WITH simple_with_stop_words_dict;
        """
    )


def downgrade() -> None:
    op.execute("DROP TEXT SEARCH CONFIGURATION simple_with_stop_words")
    op.execute("DROP TEXT SEARCH DICTIONARY simple_with_stop_words_dict")
