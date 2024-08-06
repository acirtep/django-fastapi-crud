import time

import pandas as pd
from pandas import DataFrame
from sqlalchemy import Engine, Select
from sqlalchemy import event
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from mysite import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # echo=True,
)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as error:
        await db.rollback()
        raise error
    finally:
        await db.close()


def query_to_pandas_df(session: AsyncSession, query: Select) -> DataFrame:
    conn = session.connection()
    return pd.read_sql_query(query, conn)


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())
    print("Start Query")
    for idx, val in enumerate(parameters):
        statement = statement.replace(f"${idx+1}", f"'{val}'")
    print(text(statement).compile(dialect=postgresql.dialect(), compile_kwargs={"render_postcompile": True}))


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info["query_start_time"].pop(-1)
    print("Query Complete!")
    print(f"Total Time (ms): {total*1000: .2f}")
