from fastapi import Depends, FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from pymongo import MongoClient
from routers import auth

class Payment(BaseModel):
    consultationID: int
    participantID: int
    paymentID: int
    amount: int
    status: str

app = FastAPI()
router = APIRouter()

client = MongoClient("mongodb+srv://admin:admin123@cluster0.07z4doa.mongodb.net/?retryWrites=true&w=majority")
db = client["VirtualCoffeeConsultation"]
collection = db["paymentprocessing"]

def convert_id(payment):
    payment['_id'] = str(payment['_id'])
    return payment

@router.get('/paymentprocessing')
async def read_all_payment( current_user: auth.User = Depends(auth.get_current_active_user)):
    return list(map(convert_id, collection.find()))

@router.get('/paymentprocessing/{consultation_id}')
async def read_payment(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
    payment = collection.find_one({"consultationID": consultation_id})
    if payment:
        return convert_id(payment)
    raise HTTPException(status_code=404, detail=f'Payment with consultationID {consultation_id} not found')

@router.post('/paymentprocessing')
async def add_payment(payment: Payment, current_user: auth.User = Depends(auth.get_current_active_user)):
    payment_dict = payment.dict()
    required_params = Payment.__annotations__.keys()
    provided_params = payment_dict.keys()
    
    if set(required_params).issubset(provided_params):
        existing_payment = collection.find_one({"consultationID": payment_dict['consultationID']})
        if existing_payment:
            return f"Payment for consultationID {payment_dict['consultationID']} exists."
        
        inserted_id = collection.insert_one(payment_dict).inserted_id
        if inserted_id:
            new_payment = collection.find_one({"_id": inserted_id})
            return convert_id(new_payment)
        
        raise HTTPException(status_code=404, detail=f'Failed to add payment')
    else:
        raise HTTPException(status_code=422, detail="All parameters are required")

@router.put('/paymentprocessing')
async def update_payment(payment: Payment, current_user: auth.User = Depends(auth.get_current_active_user)):
    payment_dict = payment.dict()
    result = collection.replace_one({"consultationID": payment_dict['consultationID']}, payment_dict)
    if result.modified_count > 0:
        return "Updated"
    return "Payment for consultationID not found."

@router.delete('/paymentprocessing/{consultation_id}')
async def delete_payment(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
    result = collection.delete_one({"consultationID": consultation_id})
    if result.deleted_count > 0:
        return "Deleted"
    return "Payment for consultationID not found."
