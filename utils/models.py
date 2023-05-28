from typing import Union
from pydantic import BaseModel, Field
from sqlalchemy import select

from db import location_db, database, cargo_db, car_db


class InputWeight(BaseModel):
    pick_up_zip: str
    delivery_zip: str
    weight: int = Field(ge=1, le=1000)
    description: str


class OutputWeight(BaseModel):
    id: int


class UpdateCar(BaseModel):
    id: int
    zip: str


class UpdateCargo(BaseModel):
    id: int
    weight: int = Field(ge=1, le=1000)
    description: str


class CargoDb:
    @staticmethod
    async def insert_cargo_to_db(loc_pick_up_lat: str, loc_pick_up_lng: str, delivery_lat: str, delivery_lng: str,
                                 weight: int, description: str) -> int:
        dict_post = {"loc_pick_up_lat": loc_pick_up_lat,
                     "loc_pick_up_lng": loc_pick_up_lng,
                     "delivery_lat": delivery_lat,
                     "delivery_lng": delivery_lng,
                     "weight": weight,
                     "description": description,
                     }
        query = cargo_db.insert().values(dict_post)
        id_value = await database.execute(query=query)
        return id_value

    @staticmethod
    async def get_all_cargos() -> list:
        query = select(cargo_db)
        result = await database.fetch_all(query)
        if result != []:
            result = [dict(i) for i in result]
        return result

    @staticmethod
    async def get_one_cargo(id: int) -> Union[dict, None]:
        query = select(cargo_db).where(cargo_db.columns.id == id)
        result = await database.fetch_one(query)
        if result is not None:
            result = dict(result)
        return result

    @staticmethod
    async def update_info_about_one_cargo(id: int, weight: int, description: str) -> None:
        dict_post = {"weight": weight,
                     "description": description}
        query = cargo_db.update().where(
            cargo_db.columns.id == id).values(
            dict_post)
        await database.execute(query=query)


    @staticmethod
    async def del_info_about_one_cargo(id: int) -> None:
        query = cargo_db.delete().where(
            cargo_db.columns.id == id)
        await database.execute(query=query)


class LocationDb:
    @staticmethod
    async def get_location_by_zip(zip_value: str) -> Union[dict, None]:
        query = select(location_db).where(location_db.columns.zip == zip_value)
        result = await database.fetch_one(query)
        if result is not None:
            result = dict(result)
        return result


class CarDb:
    @staticmethod
    async def get_all_cars() -> list:
        query = select(car_db)
        result = await database.fetch_all(query)
        if result != []:
            result = [dict(i) for i in result]
        return result

    @staticmethod
    async def get_one_car(id: int) -> Union[dict, None]:
        query = select(car_db).where(car_db.columns.id == id)
        result = await database.fetch_one(query)
        if result is not None:
            result = dict(result)
        return result

    @staticmethod
    async def update_info_about_one_car(id: int, loc_lat: str, loc_lng: str) -> None:
        dict_post = {"loc_lat": loc_lat,
                     "loc_lng": loc_lng}
        query = car_db.update().where(
            car_db.columns.id == id).values(
            dict_post)
        await database.execute(query=query)
