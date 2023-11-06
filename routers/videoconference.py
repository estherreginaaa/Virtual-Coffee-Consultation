from fastapi import FastAPI, HTTPException, APIRouter
import json
from pydantic import BaseModel

class VidCon(BaseModel):
	consultationID: int
	participantID: int
	advisorID: int
	hostID: int
	consultationDate: str
	consultationTime: str
	meetingPlatform: str
	meetingLink: str

json_filename="videoconference.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

# app = FastAPI()
router = APIRouter()

@router.get('/videoconference')
async def read_all_vidcon():
	return data['videoconference']


@router.get('/videoconference/{consultation_id}')
async def read_vidcon(consultation_id: int):
	for vidcon in data['videoconference']:
		print(vidcon)
		if vidcon['consultationID'] == consultation_id:
			return vidcon
	raise HTTPException(
		status_code=404, detail=f'menu not found'
	)

@router.post('/videoconference')
async def add_menu(vidcon: VidCon):
	vidcon_dict = vidcon.dict()
	vidcon_found = False
	for vidcon in data['videoconference']:
		if vidcon['consultationID'] == vidcon_dict['consultationID']:
			vidcon_found = True
			return "Consultation consultationID "+str(vidcon_dict['consultationID'])+" exists."
	
	if not vidcon_found:
		data['videoconference'].append(vidcon_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return vidcon_dict
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
# put gabisa pake web browser testnya
@router.put('/videoconference')
async def update_menu(vidcon: VidCon):
	vidcon_dict = vidcon.dict()
	vidcon_found = False
	for vidcon_idx, vidcon_item in enumerate(data['videoconference']):
		if vidcon_item['consultationID'] == vidcon_dict['consultationID']:
			vidcon_found = True
			data['videoconference'][vidcon_idx]=vidcon_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not vidcon_found:
		return "Menu consultationID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@router.delete('/videoconference/{consultation_id}')
async def delete_menu(consultation_id: int):

	vidcon_found = False
	for vidcon_idx, vidcon_item in enumerate(data['videoconference']):
		if vidcon_item['consultationID'] == consultation_id:
			vidcon_found = True
			data['videoconference'].pop(vidcon_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not vidcon_found:
		return "Video conference link for consultationID is not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
