from fastapi import FastAPI
from routers import integration_location, paymentprocessing, schedulingplatform, videoconference, auth, integration_interactivechat
import uvicorn

app = FastAPI()

app.include_router(paymentprocessing.router)
app.include_router(schedulingplatform.router)
app.include_router(videoconference.router)
app.include_router(auth.router)
app.include_router(integration_location.router)
app.include_router(integration_interactivechat.router)


if __name__== "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 8000)


