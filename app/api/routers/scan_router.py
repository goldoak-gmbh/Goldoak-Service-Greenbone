# app/api/routers/scan_router.py

##################################################################
# Importing packages                                             #
##################################################################

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.modules.greenbone.services import scan_service


##################################################################
# Defining our routers                                           #
##################################################################

router = APIRouter()

class ScanRequest(BaseModel):
    target_name: str
    hosts: str
    scan_config_id: str

@router.get("/version")
async def get_version():
    try:
        version_info = scan_service.get_version()
        return version_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan")
async def trigger_scan(request: ScanRequest):
    try:
        target_id = scan_service.create_target(request.target_name, request.hosts)
        task_id = scan_service.create_task(f"{request.target_name} Scan", target_id, request.scan_config_id)
        scan_service.start_task(task_id)
        return {"message": "Scan started", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




