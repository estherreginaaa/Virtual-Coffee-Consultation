from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from pydantic import BaseModel

SECRET_KEY = "a0cd130b49f2a477cbf1a05130529369562595b0bd85d75d7e4526bd495a2340"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
router = APIRouter()

client = MongoClient("mongodb+srv://admin:admin123@cluster0.07z4doa.mongodb.net/?retryWrites=true&w=majority")
db = client["VirtualCoffeeConsultation"]
users_collection = db["user"]

class Token(BaseModel):
    access_token: str
    token_type: str

class RegistUser(BaseModel):
    username: str 
    password: str
    name: str or None = None
    email: str or None = None

class User(BaseModel):
    username: str
    participantID: int or None = None
    email: str or None = None
    name: str or None = None
    disabled: bool or None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    return users_collection.find_one({"username": username})

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return UserInDB(**user)

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        user = users_collection.find_one({"username": username})
        if user is None:
            raise credential_exception

        return User(**user)
    except JWTError:
        raise credential_exception

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]


@router.post("/register/", response_model=Token)
async def register_user(new_user: RegistUser):
    try:
        existing_user = users_collection.find_one({"username": new_user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        last_user = users_collection.find_one(sort=[("participantID", -1)])
        last_participant_id = last_user["participantID"] if last_user else 0

        hashed_password = get_password_hash(new_user.password)

        new_user_data = {
            "username": new_user.username,
            "participantID": last_participant_id + 1,
            "name": new_user.name,
            "email": new_user.email,
            "hashed_password": hashed_password,
            "disabled": False,
        }

        inserted_user = users_collection.insert_one(new_user_data)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user_data["username"]}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error occurred during user registration: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user, please try again later")


app.include_router(router)
