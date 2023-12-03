from fastapi import Depends, FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from pymongo import MongoClient
from routers import auth

class Schedule(BaseModel):
    consultationID: int
    advisorID: int
    participantID: int
    consultationDate: str
    consultationTime: str

app = FastAPI()
router = APIRouter()

client = MongoClient("mongodb+srv://admin:admin123@cluster0.07z4doa.mongodb.net/?retryWrites=true&w=majority")
db = client["VirtualCoffeeConsultation"]
collection = db["schedulingplatform"]

def convert_id(schedule):
    schedule['_id'] = str(schedule['_id'])
    return schedule

@router.get('/schedulingplatform')
async def read_all_scheduling_platform(current_user: auth.User = Depends(auth.get_current_active_user)):
    return list(map(convert_id, collection.find()))

@router.get('/schedulingplatform/{consultation_id}')
async def read_schedulingplatform(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
    scheduling = collection.find_one({"consultationID": consultation_id})
    if scheduling:
        return convert_id(scheduling)
    raise HTTPException(status_code=404, detail=f'Consultation with ID {consultation_id} not found')

@router.post('/schedulingplatform')
async def add_menu(schedule: Schedule, current_user: auth.User = Depends(auth.get_current_active_user)):
    schedule_dict = schedule.dict()
    existing_schedule = collection.find_one({"consultationID": schedule_dict['consultationID']})
    if existing_schedule:
        return f"Consultation consultationID {schedule_dict['consultationID']} exists."
    
    inserted_id = collection.insert_one(schedule_dict).inserted_id
    if inserted_id:
        # Retrieve the inserted document to return
        new_schedule = collection.find_one({"_id": inserted_id})
        return convert_id(new_schedule)
    
    raise HTTPException(status_code=404, detail=f'Failed to add item')

@router.put('/schedulingplatform')
async def update_menu(schedule: Schedule, current_user: auth.User = Depends(auth.get_current_active_user)):
    schedule_dict = schedule.dict()
    result = collection.replace_one({"consultationID": schedule_dict['consultationID']}, schedule_dict)
    if result.modified_count > 0:
        return "Updated"
    return "Menu consultationID not found."

@router.delete('/schedulingplatform/{consultation_id}')
async def delete_menu(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
    result = collection.delete_one({"consultationID": consultation_id})
    if result.deleted_count > 0:
        return "Deleted"
    return "Menu consultationID not found."
