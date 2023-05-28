import asyncio
import random
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import database
from logs_info import logger
from routers import router_data
from data_env import name_application, version_application, main_url
from utils.models import LocationDb, CarDb

app = FastAPI(
    title=name_application,
    version=version_application,
    swagger_ui_parameters={
        "url": f"{main_url}/openapi.json",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "requestSnippetsEnabled": True,

    },
    servers=[
        {"url": main_url},
    ]
)
origins = ["*"]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def periodic_func():
    try:
        while True:
            zip_list = await LocationDb.get_zip_column()
            id_car_list = await CarDb.get_id_column()
            for i in id_car_list:
                zip_random = await LocationDb.get_location_by_zip(random.choice(zip_list))
                await CarDb.update_info_about_one_car(i, zip_random['lat'], zip_random['lng'])
            await asyncio.sleep(180)
    except Exception as e:
        logger.error("Error with periodic_func", exc_info=True)


@app.on_event("startup")
async def startup():
    await database.connect()
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_func())


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(router_data.router)


@app.get('/ping', response_model=str, include_in_schema=False)
def ping_api():
    return 'pong'


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=8000,
        reload=True
    )
