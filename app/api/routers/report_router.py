# app/api/routers/report_router.py

##################################################################
# Importing packages                                             #
##################################################################

from fastapi import APIRouter, HTTPException

from app.api.modules.greenbone.services import scan_service
from app.api.modules.greenbone.utils.gvm_parser import (
    parse_all_reports, 
    parse_report_summary
)

##################################################################
# Defining our routers                                           #
##################################################################

router = APIRouter()

@router.get("/reports/summaries")
async def get_report_summaries():
    """
    Retrieves all available reports, parses them, and returns a summary.
    """
    try:
        # Call the service function to retrieve all reports
        reports_response = scan_service.get_all_reports()
        # Use our parser function to extract a summary for each report
        summaries = parse_all_reports(reports_response)
        return {"reports": summaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

