from  fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection,HashModel
app=FastAPI()




origins = ["localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis=


class Delivery(HashModel):
    budget:int=0
    notes:str=""

    class Meta:
        database:redis

