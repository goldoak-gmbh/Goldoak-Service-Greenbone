# app/main.py

##################################################################
# Importing packages                                             #
##################################################################

import logging
from fastapi import FastAPI

from app.api.modules.greenbone.utils.report_worker import run_report_worker
from app.api.routers import scan_router, report_router

##################################################################
# Defining our logger                                            #
##################################################################

logging.basicConfig(
    level=logging.INFO,  # or DEBUG if we want more verbosity
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

##################################################################
# APP settings                                                   #
##################################################################

app = FastAPI(
    title="Goldoak Service Greenbone version 0.6",
    description="With this module you can gather information of the greenbone vulnerability manager and work with it."
)

# Our routers
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

app.include_router(scan_router.router, prefix="/api/greenbone")   # Starting a Scan 
app.include_router(report_router.router, prefix="/api/greenbone") # Displaying Reports 

##################################################################
# Startup Event: Launch Workers                                  #
##################################################################

@app.on_event("startup")
async def startup_event():
    # Start the report worker; you can add more workers as needed.
    run_report_worker() 



