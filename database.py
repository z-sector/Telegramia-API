from fastapi import status, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import motor.motor_asyncio

from config import DB_PASSWORD

client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb+srv://mezgoodle:{DB_PASSWORD}@telegramia.jkq5x.mongodb.net/'
                                                f'telegramia?retryWrites=true&w=majority')
db = client['Telegramia']


async def create_document(data: BaseModel, collection: str):
    data = jsonable_encoder(data)
    new_object = await db[collection].insert_one(data)
    created_object = await db[collection].find_one({"_id": new_object.inserted_id})
    if not created_object:
        raise HTTPException(status_code=404, detail='Object has not created')
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_object)


async def get_all_objects(collection: str, response: Response):
    objects = await db[collection].find().to_list(1000)
    if not objects:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail': 'There are no objects'}
    return objects


async def get_object(query: dict, collection: str):
    if (object := await db[collection].find_one(query)) is not None:
        return object
    raise HTTPException(status_code=404, detail='Object has not found')


async def update_object(query: dict, object: BaseModel, collection: str):
    object = {k: v for k, v in object.dict().items() if v is not None}

    if len(object) >= 1:
        update_result = await db[collection].update_one(query, {"$set": object})

        if update_result.modified_count == 1:
            if (updated_object := await db[collection].find_one(query)) is not None:
                return updated_object

    if (existing_object := await db[collection].find_one(query)) is not None:
        return existing_object

    raise HTTPException(status_code=404, detail='Object has not found')


async def delete_object(query: dict, collection: str):
    delete_result = await db[collection].delete_one(query)

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail='Object has not found')
