import asyncio
from datetime import datetime
from itertools import product
from os import environ
import uuid

from pydantic import BaseModel
from sqlalchemy import text

from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine

fake = Faker()
num = 1000000

environ["PGDATABASE"] = "test"
engine = create_async_engine(
    "postgresql+asyncpg://",
    pool_size=50,
    max_overflow=1,
    pool_timeout=360,
    pool_pre_ping=True,
    # echo=True,
)

"""
-- Tables
CREATE TABLE method1 (
  id SERIAL PRIMARY KEY,
  primary_key_id UUID,
  data TEXT,
  record_date TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_method1_primary_key_id ON method1(primary_key_id);

CREATE TABLE method2 (
  id SERIAL PRIMARY KEY,
  primary_key_id UUID,
  data TEXT,
  record_date TIMESTAMP DEFAULT NOW(),
  is_outdated BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_method2_primary_key_id ON method2(primary_key_id);

CREATE TABLE method3_data (
  id SERIAL PRIMARY KEY,
  primary_key_id UUID,
  data TEXT,
  record_date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE method3_primary (
  primary_key_id UUID PRIMARY KEY,
  current_data_id INTEGER REFERENCES method3_data(id)
);

CREATE INDEX idx_method3_data_primary_key_id ON method3_data(primary_key_id);
"""


class TestModel(BaseModel):
    primary_key: uuid.UUID
    data: str


def create_data():
    data_rows = [
        TestModel(
            primary_key=uuid.uuid4(),
            data=fake.text(),
        )
        for i in range(num)
    ]

    update_rows = [
        TestModel(
            primary_key=i.primary_key,
            data=fake.text(),
        )
        for i in data_rows
    ]

    update2_rows = [
        TestModel(
            primary_key=i.primary_key,
            data=fake.text(),
        )
        for i in data_rows
    ]
    return data_rows, update_rows, update2_rows


async def upsert_method1(data: list[TestModel]):
    db_data = [i.dict() for i in data]
    async with engine.begin() as conn:
        return await conn.execute(
            text(
                """
            INSERT INTO method1 (primary_key_id, data)
            VALUES (:primary_key, :data)
            """
            ),
            db_data,
        )


async def upsert_method2(data: list[TestModel]):
    db_data = [i.dict() for i in data]
    primary_keys = [i.primary_key for i in data]
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
            UPDATE method2 SET is_outdated = TRUE
            WHERE primary_key_id = ANY(:primary_keys) and is_outdated = FALSE
            """
            ).bindparams(primary_keys=primary_keys)
        )
        return await conn.execute(
            text(
                """
            INSERT INTO method2 (primary_key_id, data)
            VALUES (:primary_key, :data)
            """
            ),
            db_data,
        )


async def upsert_method3(data: list[TestModel]):
    db_data = [i.dict() for i in data]

    for datum in db_data:
        async with engine.begin() as conn:
            output = (
                await conn.execute(
                    text(
                        """
                INSERT INTO method3_data (primary_key_id, data)
                VALUES (:primary_key, :data)
                RETURNING id
                """
                    ).bindparams(**datum)
                )
            ).fetchone()
            if output:
                id = output.id
                await conn.execute(
                    text(
                        """
                    INSERT INTO method3_primary (primary_key_id, current_data_id)
                    VALUES (:primary_key, :current_data_id)
                    ON CONFLICT (primary_key_id)
                    DO UPDATE SET current_data_id = EXCLUDED.current_data_id
                    """
                    ).bindparams(primary_key=datum["primary_key"], current_data_id=id)
                )


async def chunk_data(data, func):
    time_start = datetime.now()
    chunk_size = 1000
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    await asyncio.gather(*[func(chunk) for chunk in chunks])
    print(f"{func.__name__} took {datetime.now()-time_start}")


async def run_all():
    data_rows, update_rows, update2_rows = create_data()

    for func, data in product(
        [upsert_method1, upsert_method2, upsert_method3],
        [data_rows, update_rows, update2_rows],
    ):
        await chunk_data(data, func)


asyncio.run(run_all())


"""
upsert_method1 took 0:00:16.409400
upsert_method1 took 0:00:14.028337
upsert_method1 took 0:00:14.038094
upsert_method2 took 0:00:16.710914
upsert_method2 took 0:00:19.777441
upsert_method2 took 0:00:20.309022
upsert_method3 took 0:18:22.237005
upsert_method3 took 0:18:26.125393
upsert_method3 took 0:18:27.617683
"""

"""
WITH relevant as
(
	SELECT *, ROW_NUMBER() OVER(PARTITION BY m.primary_key_id ORDER BY id DESC) as row_num
	FROM method1 m
	JOIN (
			SELECT primary_key_id
			FROM rand_p_keys
			ORDER BY RANDOM()
			LIMIT 1000
	) AS random_keys ON m.primary_key_id = random_keys.primary_key_id
)
SELECT * from relevant
WHERE row_num = 1


SELECT *
FROM method2 m
JOIN (
		SELECT primary_key_id
		FROM rand_p_keys
		ORDER BY RANDOM()
		LIMIT 1000
) AS random_keys ON m.primary_key_id = random_keys.primary_key_id and m.is_outdated IS FALSE


SELECT *
FROM method3_primary m
JOIN (
		SELECT primary_key_id
		FROM rand_p_keys
		ORDER BY RANDOM()
		LIMIT 1000
) AS random_keys ON m.primary_key_id = random_keys.primary_key_id
JOIN method3_data m2 ON m.current_data_id = m2.id

query times
    1000    10k     100k
m1  .26     .46     3.7
m2  .26     .51     2.7
m3  .26     .54     2.2

"""
