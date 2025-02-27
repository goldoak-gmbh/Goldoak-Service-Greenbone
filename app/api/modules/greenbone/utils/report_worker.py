# app/api/modules/greenbone/utils/report_worker.py

##################################################################
# Importing packages                                             #
##################################################################

import os
import datetime
import logging
import subprocess
import xmltodict
from apscheduler.schedulers.background import BackgroundScheduler

from app.api.modules.greenbone.services.scan_service.py import get_all_reports
from app.api.core.config import (
    GVM_SOCKET_PATH, 
    REPORTS_DIR, 
    USER, 
    PASSWORD
)

##################################################################
# Defining our Logger and Worker                                 #
##################################################################

logger = logging.getLogger(__name__)

def run_report_worker():
    """
    Starts a background scheduler to run fetch_and_save_report_ids() every 10 minutes.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_save_report_ids, 'interval', minutes=1)
    scheduler.start()
    logger.info("Report processing scheduler started.")
    return scheduler

##################################################################
# Workflow                                                       #
# 1) Fetch overview of report ids via get_all_reports            #
# 2) Save the report ids in a file                               #
##################################################################

##################################################################
# Defining our methods the report worker will be using           #
##################################################################

# Hands the report IDs over to the function save_report_ids()
def fetch_and_save_report_ids() -> str:
    """
    Fetches all available reports via get_all_reports(), extracts the report IDs,
    and saves them to a file.
    Returns the path to the saved file or None if no report IDs are found.
    """
    raw_response = get_all_reports()
    if not raw_response:
        logger.error("No response from get_all_reports()")
        return None
    report_ids = extract_report_ids(raw_response)
    if not report_ids:
        logger.info("No report IDs found in response.")
        return None
    return save_report_ids(report_ids)

# Extracts the Report IDs
def extract_report_ids(raw_response: dict) -> list:
    """
    Given the raw response dictionary from get_all_reports(),
    extract the report IDs as a list.
    """
    # Get the report section from the parsed XML response.
    reports = raw_response.get("get_reports_response", {}).get("report", [])
    if not isinstance(reports, list):
        reports = [reports]
    # Extract the report IDs (stored in the "@id" attribute)
    report_ids = [report.get("@id") for report in reports if report.get("@id")]
    return report_ids

# Saves reports in our directory
def save_report_ids(report_ids: list) -> str:
    """
    Saves the list of report IDs to a file in REPORTS_DIR.
    The filename includes a timestamp for uniqueness.
    Returns the full path to the saved file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"report_ids_{timestamp}.txt"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        for report_id in report_ids:
            f.write(report_id + "\n")
    logger.info(f"Saved report IDs to {filepath}")
    return filepath
    