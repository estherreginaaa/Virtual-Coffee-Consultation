from fastapi import Depends, FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from pymongo import MongoClient
from routers import auth 

class VidCon(BaseModel):
    consultationID: int
    participantID: int
    advisorID: int
    hostID: int
    consultationDate: str
    consultationTime: str
    meetingPlatform: str
    meetingLink: str

app = FastAPI()
router = APIRouter()

client = MongoClient("mongodb+srv://admin:admin123@cluster0.07z4doa.mongodb.net/?retryWrites=true&w=majority")
db = client["VirtualCoffeeConsultation"]
collection = db["videoconference"]

def convert_id(vidcon):
    vidcon['_id'] = str(vidcon['_id'])
    return vidcon

@router.get('/videoconference')
async def read_all_vidcon(current_user: auth.User = Depends(auth.get_current_active_user)):
    return list(map(convert_id, collection.find()))

@router.get('/videoconference/{consultation_id}')
async def read_vidcon(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
    vidcon = collection.find_one({"consultationID": consultation_id})
    if vidcon:
        return convert_id(vidcon)
    raise HTTPException(status_code=404, detail=f'VidCon with consultationID {consultation_id} not found')

@router.post('/videoconference')
async def add_vidcon(vidcon: VidCon, current_user: auth.User = Depends(auth.get_current_active_user)):
    vidcon_dict = vidcon.dict()
    required_params = VidCon.__annotations__.keys()
    provided_params = vidcon_dict.keys()
    
    # Check if all required parameters are provided
    if set(required_params).issubset(provided_params):
        existing_vidcon = collection.find_one({"consultationID": vidcon_dict['consultationID']})
        if existing_vidcon:
            return f"VidCon for consultationID {vidcon_dict['consultationID']} exists."
        
        inserted_id = collection.insert_one(vidcon_dict).inserted_id
        if inserted_id:
            new_vidcon = collection.find_one({"_id": inserted_id})
            return convert_id(new_vidcon)
        
        raise HTTPException(status_code=404, detail=f'Failed to add VidCon')
    else:
        raise HTTPException(status_code=422, detail="All parameters are required")

@router.put('/videoconference')
async def update_vidcon(vidcon: VidCon, current_user: auth.User = Depends(auth.get_current_active_user)):
    vidcon_dict = vidcon.dict()
    result = collection.replace_one({"consultationID": vidcon_dict['consultationID']}, vidcon_dict)
    if result.modified_count > 0:
        return "Updated"
    return "VidCon for consultationID not found."

@router.delete('/videoconference/{consultation_id}')
async def delete_vidcon(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
    result = collection.delete_one({"consultationID": consultation_id})
    if result.deleted_count > 0:
        return "Deleted"
    return "VidCon for consultationID not found."
