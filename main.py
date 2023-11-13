from fastapi import FastAPI
from routers import paymentprocessing, schedulingplatform, videoconference, auth
import uvicorn

app = FastAPI()

app.include_router(paymentprocessing.router)
app.include_router(schedulingplatform.router)
app.include_router(videoconference.router)
app.include_router(auth.router)

if __name__== "_main_":
    uvicorn.run(app, host="0.0.0.0", port = 8000)


