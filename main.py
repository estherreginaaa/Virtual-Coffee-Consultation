from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    integration_location,
    paymentprocessing,
    schedulingplatform,
    videoconference,
    auth,
    integration_interactivechat,
)
import uvicorn

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(paymentprocessing.router)
app.include_router(schedulingplatform.router)
app.include_router(videoconference.router)
app.include_router(auth.router)
app.include_router(integration_location.router)
app.include_router(integration_interactivechat.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
