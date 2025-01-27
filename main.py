from fastapi import FastAPI
import uvicorn

from src.routes import contacts
from src.routes import auth

app = FastAPI()

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)