# app/main.py

##################################################################
# Importing packages                                             #
##################################################################
from fastapi import FastAPI

from app.api.routers import scan_router
from app.api.core import config

##################################################################
# APP settings                                                   #
##################################################################
app = FastAPI(
    title="Goldoak Service Greenbone version 0.1",
    description="With this module you can gather information of the greenbone vulnerability manager and work with it."
)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

app.include_router(scan_router.router, prefix="/api/greenbone")

