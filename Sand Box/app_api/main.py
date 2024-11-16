from fastapi import FastAPI, File, UploadFile, Path, Query
from io import BytesIO
from pymongo import MongoClient, ASCENDING, ReturnDocument, UpdateMany, GEO2D, GEOSPHERE
from pymongo.errors import PyMongoError, ConnectionFailure

conn = MongoClient("mongodb://admin:Tzf4GKgIFAc@mongodb:27017")

app = FastAPI()

@app.get("/api/v1/sample-db")
async def sample():
    db = conn["local"]
    coll = db["startup_log"]
    data = coll.find({}, projection={"_id": 0}, limit=10)
    result = [_ for _ in data]
    return result