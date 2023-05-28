from databases import Database

from sqlalchemy import create_engine, MetaData, Column, Integer, String, Table
from data_env import user_value, password_value, host_value, port_value, database_value

SQLALCHEMY_DATABASE_URL = f'postgresql://{user_value}:{password_value}@{host_value}:{port_value}/{database_value}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()


cargo_db = Table(
    "cargo_db",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("loc_pick_up_lat", String),
    Column("loc_pick_up_lng", String),
    Column("delivery_lat", String),
    Column("delivery_lng", String),
    Column("weight", Integer),
    Column("description", String),
)

car_db = Table(
    "car_db",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("unique_number", String, unique=True),
    Column("loc_lat", String),
    Column("loc_lng", String),
    Column("load_capacity", Integer),
)

location_db = Table(
    "location_db",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("city", String),
    Column("state_name", String),
    Column("zip", String),
    Column("lat", String),
    Column("lng", String),
)

database = Database(SQLALCHEMY_DATABASE_URL)
