from  fastapi import FastAPI,Request
import json
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection,HashModel
import consumers
app=FastAPI()



origins = [
    "http://localhost:3000",
    "localhost:3000",
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis=get_redis_connection(
    
                            )



class Delivery(HashModel):
    budget:int=0
    notes:str=""

    class Meta:
        database:redis

class Event(HashModel):
    delivery_id:str=None
    type:str
    data:str

    class Meta:
        database:redis


@app.post("/deliveries/create")
async def  create(request:Request):
    body=await request.json()
    delivery=Delivery(budget=body['data']['budget'],notes=body['data']['notes']).save()
    event=Event( delivery_id=delivery.pk, type=body['type'], data=json.dumps(body['data'])).save()
    state=consumers.CONSUMERS[event.type]({},event)
    redis.set(f'delivery:{delivery.pk}',json.dumps(state))   #wont save in a db, but in redis cache
    return state


@app.get("/deliveries/{pk}/status")
async def get_state(pk:str):
    state=redis.get(f'delivery:{pk}')
    if state is not None:
        return json.loads(state)
    state=build_state(pk)
    redis.set(f'delivery:{pk}',json.dumps(state))
    return {}

#Rebuild state 
def build_state(pk:str):
    pks=Event.all_pks()
    all_events=[Event.get(pk) for pk in pks]
    events=[event for event in all_events if event.delivery_id==pk]
    state={}
    for event in events:
        state=consumers.CONSUMERS[event.type](state,event)
    return state

@app.post("/event")
async def dispatch(request:Request):
    body= await request.json()
    delivery_id=body['delivery_id']
    event=Event( delivery_id=delivery_id, type=body['type'], data=json.dumps(body['data'])).save()
    state=await get_state(delivery_id)
    newState=consumers.CONSUMERS[event.type](state,event)
    redis.set(f'delivery:{delivery_id}',json.dumps(newState))
    return newState

