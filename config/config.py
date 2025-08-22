from typing import AsyncGenerator
import asyncpg

from config.settings import Setting


async def get_postgres_cursor() -> AsyncGenerator[asyncpg.Connection, None]:
    conn: asyncpg.Connection = await asyncpg.connect(
        user=Setting().POSTGRES_USER,
        password=Setting().POSTGRES_PASSWORD,
        database=Setting().POSTGRES_DATABASE,
        host=Setting().POSTGRES_HOST,
        port=Setting().POSTGRES_PORT
    )

    print(conn)

    try: 
        yield conn
    except:
        await conn.close()
        