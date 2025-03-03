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

# Getting version infor from the GVM-Socket
@router.get("/version")
async def get_version():
    try:
        version_info = scan_service.get_version()
        return version_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Display overview of all available reports
@router.get("/reports")
async def fetch_all_reports():
    try:
        reports = scan_service.get_all_reports()
        # Process the XML response to extract a list of report IDs, e.g.:
        report_list = reports.get("get_reports_response", {}).get("report", [])
        # Ensure report_list is always a list
        if not isinstance(report_list, list):
            report_list = [report_list]
        return {"reports": report_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start a Vulnerability Scan
@router.post("/scan")
async def trigger_scan(request: ScanRequest):
    try:
        target_id = scan_service.create_target(request.target_name, request.hosts)
        task_id = scan_service.create_task(f"{request.target_name} Scan", target_id, request.scan_config_id)
        scan_service.start_task(task_id)
        return {"message": "Scan started", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



