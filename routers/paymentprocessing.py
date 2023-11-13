from fastapi import Depends, FastAPI, HTTPException, APIRouter
import json
from pydantic import BaseModel
from routers import auth


class Payment(BaseModel):
    consultationID: int
    participantID: int
    paymentID: int
    amount: int
    status: str

json_filename="paymentprocessing.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

# app = FastAPI()
router = APIRouter()

@router.get('/paymentprocessing')
async def read_all_payment(current_user: auth.User = Depends(auth.get_current_active_user)):
	return data['paymentprocessing']


@router.get('/paymentprocessing/{consultation_id}')
async def read_vidcon(consultation_id: int,current_user: auth.User = Depends(auth.get_current_active_user) ):
	for payment in data['paymentprocessing']:
		print(payment)
		if payment['consultationID'] == consultation_id:
			return payment
	raise HTTPException(
		status_code=404, detail=f'menu not found'
	)

@router.post('/paymentprocessing')
async def add_menu(payment: Payment, current_user: auth.User = Depends(auth.get_current_active_user)):
	payment_dict = payment.dict()
	payment_found = False
	for payment in data['paymentprocessing']:
		if payment['consultationID'] == payment_dict['consultationID']:
			payment_found = True
			return "Consultation consultationID "+str(payment_dict['consultationID'])+" exists."
	
	if not payment_found:
		data['paymentprocessing'].append(payment_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return payment_dict
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
# put gabisa pake web browser testnya
@router.put('/paymentprocessing')
async def update_menu(payment: Payment, current_user: auth.User = Depends(auth.get_current_active_user)):
	payment_dict = payment.dict()
	payment_found = False
	for payment_idx, payment_item in enumerate(data['paymentprocessing']):
		if payment_item['consultationID'] == payment_dict['consultationID']:
			payment_found = True
			data['paymentprocessing'][payment_idx]=payment_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not payment_found:
		return "Menu consultationID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@router.delete('/paymentprocessing/{consultation_id}')
async def delete_menu(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):

	payment_found = False
	for payment_idx, payment_item in enumerate(data['paymentprocessing']):
		if payment_item['consultationID'] == consultation_id:
			payment_found = True
			data['paymentprocessing'].pop(payment_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not payment_found:
		return "Video conference link for consultationID is not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
