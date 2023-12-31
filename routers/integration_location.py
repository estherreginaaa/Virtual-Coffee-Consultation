from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests
from routers import auth


app = FastAPI()
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

virtual_hotel_tour = "http://virtualhoteltourservice.bug5gmc4dkc5g2d2.southeastasia.azurecontainer.io:8000"


username = "admin"
password = "admin200"

def get_access_token():
    login_payload = {"username": username, "password": password}
    token_response = requests.post(f"{virtual_hotel_tour}/token", data=login_payload)
    
    if token_response.status_code == 200:
        return token_response.json().get("access_token")
    else:
        raise HTTPException(status_code=token_response.status_code, detail="Login failed")


def get_and_filter_location():
    try:
        url = f"{virtual_hotel_tour}/location"
        
        headers = {'Authorization': f'Bearer {get_access_token()}'}
        response = requests.get(url, headers=headers)
        api_data = response.json()

        if isinstance(api_data, list):
            filtered_locations = [
                location for location in api_data
                if 'relax' in location['description'].lower() or 'rest' in location['description'].lower()
            ]

            return {'location': filtered_locations}
        else:
            raise ValueError("Unexpected API response format")

    except Exception as e:
        print(f"Error in get_and_filter_location: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/get_virtual_coffee_recommendationlocation")
async def get_virtual_coffee_rec_location(current_user: auth.User = Depends(auth.get_current_active_user)):
    return get_and_filter_location()


