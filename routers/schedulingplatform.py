from fastapi import Depends, FastAPI, HTTPException, APIRouter
import json
from pydantic import BaseModel
from routers import auth

class Schedule(BaseModel):
	consultationID: int
	advisorID: int
	participantID: int
	consultationDate: str
	consultationTime: str

json_filename="schedulingplatform.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = FastAPI()
router = APIRouter()

@router.get('/schedulingplatform')
async def read_all_scheduling_platform(current_user: auth.User = Depends(auth.get_current_active_user)):
	return data['schedulingplatform']


@router.get('/schedulingplatform/{consultation_id}')
async def read_schedulingplatform(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):
	for scheduling in data['schedulingplatform']:
		print(scheduling)
		if scheduling['consultationID'] == consultation_id:
			return scheduling
	raise HTTPException(
		status_code=404, detail=f'menu not found'
	)

@router.post('/schedulingplatform')
async def add_menu(schedule: Schedule, current_user: auth.User = Depends(auth.get_current_active_user)):
	schedule_dict = schedule.dict()
	schedule_found = False
	for scheduling in data['schedulingplatform']:
		if scheduling['consultationID'] == schedule_dict['consultationID']:
			schedule_found = True
			return "Consultation consultationID "+str(schedule_dict['consultationID'])+" exists."
	
	if not schedule_found:
		data['schedulingplatform'].append(schedule_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return schedule_dict
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
# put gabisa pake web browser testnya
@router.put('/schedulingplatform')
async def update_menu(schedule: Schedule, current_user: auth.User = Depends(auth.get_current_active_user)):
	schedule_dict = schedule.dict()
	schedule_found = False
	for schedule_idx, schedule_item in enumerate(data['schedulingplatform']):
		if schedule_item['consultationID'] == schedule_dict['consultationID']:
			item_found = True
			data['schedulingplatform'][schedule_idx]=schedule_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not schedule_found:
		return "Menu consultationID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@router.delete('/schedulingplatform/{consultation_id}')
async def delete_menu(consultation_id: int, current_user: auth.User = Depends(auth.get_current_active_user)):

	schedule_found = False
	for schedule_idx, schedule_item in enumerate(data['schedulingplatform']):
		if schedule_item['consultationID'] == consultation_id:
			schedule_found = True
			data['schedulingplatform'].pop(schedule_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not schedule_found:
		return "Menu consultationID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
