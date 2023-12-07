from fastapi import FastAPI, APIRouter, HTTPException, Depends
import requests
from pymongo import MongoClient
from fastapi.security import OAuth2PasswordBearer
from routers import auth
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()

mongo_connection_string = "mongodb+srv://admin:admin123@cluster0.07z4doa.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_connection_string)
db = client["VirtualCoffeeConsultation"] 
collection = db["interactionLog"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

virtual_hotel_tour = "http://127.0.0.1:8888"

username = "admin"
password = "admin200"

class Item(BaseModel):
    interactionLog_id: int
    user_id: int
    staff_id: int
    interaction_type: str
    message: str
    interaction_time: str

def get_access_token():
    login_payload = {"username": username, "password": password}
    token_response = requests.post(f"{virtual_hotel_tour}/token", data=login_payload)
    
    if token_response.status_code == 200:
        return token_response.json().get("access_token")
    else:
        raise HTTPException(status_code=token_response.status_code, detail="Login failed")


@router.post("/interactive_coffee_consultation_chat")
async def interactive_coffee_consultation_chat(item: Item, current_user: auth.User = Depends(auth.get_current_active_user)):
    # Convert the Pydantic model to a dictionary
    item_dict = item.dict()

    url = "http://127.0.0.1:8888/interactionLog"
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    response = requests.post(url, json=item_dict, headers=headers)

    if response.status_code == 200:
        store_interactionLog_in_mongodb(item_dict)
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to post data to friend's API")

def store_interactionLog_in_mongodb(item_dict: dict):
    collection.insert_one(item_dict)

@router.get("/get_interactionLog")
async def get_interactionLog():
    all_interaction_logs = list(collection.find({}, {'_id': 0}))

    if not all_interaction_logs:
        raise HTTPException(status_code=404, detail="No interaction logs found in the database")

    return {"interactionLogs": all_interaction_logs}