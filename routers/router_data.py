from fastapi import APIRouter
from starlette.responses import JSONResponse
from geopy.distance import geodesic

from logs_info import logger
from utils.models import InputWeight, LocationDb, OutputWeight, CargoDb, CarDb, UpdateCar, UpdateCargo, FilterCargos

router = APIRouter(
    prefix="/database",
    tags=['database']
)


@router.post("/add_cargo", status_code=200, response_model=OutputWeight)
async def add_cargo_to_db(input_data: InputWeight):
    try:
        if input_data.pick_up_zip == input_data.delivery_zip:
            logger.info("Parameters must not match")
            return JSONResponse(status_code=400, content={"detail": "Parameters must not match"})
        pick_up_zip = await LocationDb.get_location_by_zip(input_data.pick_up_zip)
        if pick_up_zip is None:
            logger.info("pick_up_zip is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "pick_up_zip is not exist"})
        delivery_zip = await LocationDb.get_location_by_zip(input_data.delivery_zip)
        if delivery_zip is None:
            logger.info("delivery_zip is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "delivery_zip is not exist"})
        id_value = await CargoDb.insert_cargo_to_db(pick_up_zip["lat"], pick_up_zip["lng"], delivery_zip["lat"],
                                                    delivery_zip["lng"],
                                                    input_data.weight, input_data.description)
        return {"id": id_value}
    except Exception:
        logger.error("add_cargo_to_db has error", exc_info=True)


@router.get("/get_info_about_all_cargos", status_code=200, response_model=list)
async def get_list_all_cargos():
    try:
        list_cargos = await CargoDb.get_all_cargos()
        list_cars = await CarDb.get_all_cars()
        if list_cargos != [] and list_cars != []:
            list_cargos_info = []
            for i in list_cargos:
                car_counter = 0
                loc_cargo = (float(i['loc_pick_up_lat']), float(i['loc_pick_up_lng']))
                for j in list_cars:
                    loc_car = (float(j['loc_lat']), float(j['loc_lng']))
                    if geodesic(loc_cargo, loc_car).miles <= 450:
                        car_counter += 1
                list_cargos_info.append(
                    {"cargo_id": i['id'], "pick_up": loc_cargo,
                     "delivery": (float(i['delivery_lat']), float(i['delivery_lng'])),
                     "available_car": car_counter})
            return list_cargos_info
    except Exception:
        logger.error("get_info_about_all_cargos has error", exc_info=True)


@router.get("/get_info_about_one_cargo", status_code=200, response_model=dict)
async def get_info_about_one_cargo(id: int):
    try:
        info_cargo = await CargoDb.get_one_cargo(id)
        if info_cargo is None:
            logger.info("cargo is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "cargo is not exist"})
        list_cars = await CarDb.get_all_cars()
        if list_cars is None:
            logger.info("list cars is empty")
            return JSONResponse(status_code=404,
                                content={"detail": "list cars is empty"})
        info_about_cars = []
        loc_cargo = (float(info_cargo['loc_pick_up_lat']), float(info_cargo['loc_pick_up_lng']))
        for j in list_cars:
            loc_car = (float(j['loc_lat']), float(j['loc_lng']))
            info_about_cars.append({j["unique_number"]: geodesic(loc_cargo, loc_car).miles})
        list_cargos_info = {"cargo_id": info_cargo['id'], "pick_up": loc_cargo,
                            "delivery": (float(info_cargo['delivery_lat']), float(info_cargo['delivery_lng'])),
                            "weight": info_cargo["weight"], "description": info_cargo["description"],
                            "list_car": info_about_cars}
        return list_cargos_info
    except Exception:
        logger.error("get_info_about_one_cargo has error", exc_info=True)


@router.put("/update_info_about_car", status_code=200, response_model=dict)
async def put_info_about_one_car(input_data: UpdateCar):
    try:
        info_car = await CarDb.get_one_car(input_data.id)
        if info_car is None:
            logger.info("car is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "car is not exist"})
        info_location = await LocationDb.get_location_by_zip(input_data.zip)
        if info_location is None:
            logger.info("zip is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "zip is not exist"})
        await CarDb.update_info_about_one_car(input_data.id, info_location["lat"], info_location["lng"])
        return {"detail": "data updated"}
    except Exception:
        logger.error("put_info_about_one_car has error", exc_info=True)


@router.put("/update_info_about_cargo", status_code=200, response_model=dict)
async def put_info_about_one_cargo(input_data: UpdateCargo):
    try:
        info_cargo = await CargoDb.get_one_cargo(input_data.id)
        if info_cargo is None:
            logger.info("cargo is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "cargo is not exist"})
        await CargoDb.update_info_about_one_cargo(input_data.id, input_data.weight, input_data.description)
        return {"detail": "data updated"}
    except Exception:
        logger.error("get_info_about_one_cargo has error", exc_info=True)


@router.delete("/delete_cargo", status_code=200, response_model=dict)
async def delete_info_about_one_cargo(id: int):
    try:
        info_cargo = await CargoDb.get_one_cargo(id)
        if info_cargo is None:
            logger.info("cargo is not exist")
            return JSONResponse(status_code=404,
                                content={"detail": "cargo is not exist"})
        await CargoDb.del_info_about_one_cargo(id)
        return {"detail": "data deleted"}
    except Exception:
        logger.error("delete_info_about_one_cargo has error", exc_info=True)

@router.post("/filter_cargos", status_code=200, response_model=list)
async def filter_weight_miles_cargos(input_data: FilterCargos):
    try:
        list_cargos = await CargoDb.get_all_cargos()
        list_cars = await CarDb.get_all_cars()
        if list_cargos != [] and list_cars != []:
            list_cargos_info = []
            for i in list_cargos:
                car_counter = 0
                loc_cargo = (float(i['loc_pick_up_lat']), float(i['loc_pick_up_lng']))
                for j in list_cars:
                    loc_car = (float(j['loc_lat']), float(j['loc_lng']))
                    if input_data.miles_min is not None and input_data.miles_max is not None:
                        if input_data.miles_min <= geodesic(loc_cargo, loc_car).miles <= input_data.miles_max:
                            car_counter += 1
                    elif input_data.miles_min is None and input_data.miles_max is not None:
                        if geodesic(loc_cargo, loc_car).miles <= input_data.miles_max:
                            car_counter += 1
                    elif input_data.miles_min is not None and input_data.miles_max is None:
                        if input_data.miles_min <= geodesic(loc_cargo, loc_car).miles:
                            car_counter += 1
                    else:
                        car_counter += 1
                if car_counter != 0:
                    if input_data.weight_min is not None and input_data.weight_max is not None:
                        if input_data.weight_min <= i["weight"] <= input_data.weight_max:
                            list_cargos_info.append(
                                {"cargo_id": i['id'],
                                 "weight": i["weight"],
                                 "available_car": car_counter})
                    elif input_data.weight_min is None and input_data.weight_max is not None:
                        if i["weight"] <= input_data.weight_max:
                            list_cargos_info.append(
                                {"cargo_id": i['id'],
                                 "weight": i["weight"],
                                 "available_car": car_counter})
                    elif input_data.weight_min is not None and input_data.weight_max is None:
                        if input_data.weight_min <= i["weight"]:
                            list_cargos_info.append(
                                {"cargo_id": i['id'],
                                 "weight": i["weight"],
                                 "available_car": car_counter})
                    else:
                        list_cargos_info.append(
                            {"cargo_id": i['id'],
                             "weight": i["weight"],
                             "available_car": car_counter})
            return list_cargos_info
    except Exception:
        logger.error("filter_weight_miles_cargos has error", exc_info=True)