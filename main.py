from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import uvicorn
import redis.asyncio as redis

from src.routes import contacts, users, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix='/api')


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)