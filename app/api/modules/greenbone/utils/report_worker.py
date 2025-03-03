# app/api/modules/greenbone/utils/report_worker.py

##################################################################
# Importing packages                                             #
##################################################################

# General
import os
import json
import glob
import shutil
import datetime
import logging
import subprocess
import xmltodict
from apscheduler.schedulers.background import BackgroundScheduler

# Our packages
from app.api.modules.greenbone.utils.es_ingest import ingest_parsed_reports
from app.api.modules.greenbone.utils.gvm_parser import (
    parse_xml_to_json
)

from app.api.modules.greenbone.services.scan_service import (
    get_all_reports,
    run_gvm_command
)

from app.api.core.config import (
    GVM_SOCKET_PATH, 
    REPORTS_DIR,
    ARCHIVE_DIR,
    PARSED_DIR,
    DETAILED_REPORTS_DIR,
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

    # Schedule the job to fetch and save report IDs
    scheduler.add_job(fetch_and_save_report_ids, 'interval', minutes=60)
    
    # Schedule the job to fetch and save the report-task mapping
    scheduler.add_job(fetch_and_save_report_task_mapping, 'interval', minutes=60)

    # Load the mapping and fetch detailed reports
    scheduler.add_job(process_all_detailed_reports, 'interval', minutes=1)

    # Parse the XML files and save them
    scheduler.add_job(process_xml_reports, 'interval', minutes=5)

    # Ingest parsed files into elastic
    scheduler.add_job(ingest_parsed_reports, 'interval', minutes=10)

    scheduler.start()
    logger.info("Report processing scheduler started.")
    return scheduler

###################################################################
# Workflow                                                        #
# 1) Fetch overview of report ids via get_all_reports             #
# 2) Save the report ids in a file                                #
# 3) For each entry in this file fetch the task_id of each report #
# 4) Create another file to save the mapping between both ids     #
# 5) Fetch detailed report via gvm and save the output            #
# 6) Parse the report and save the JSON file                      # 
# 7) Ingest the JSON file into elastic                            #
###################################################################

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
    logger.info("Successfully saved report IDs.")
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

##################################################################
# Defining our methods the report worker will be using           #
#                                                                #
# This section contains methods for mapping the report_id with   #
# the task_id                                                    #
##################################################################

# Main function to fetch, save and do a mapping or report_id and task_id
def fetch_and_save_report_task_mapping() -> dict:
    """
    Fetches all available reports via get_all_reports(),
    extracts a mapping of report IDs to task IDs,
    and saves this mapping to a file.
    Returns the mapping dictionary.
    """
    raw_response = get_all_reports()
    if not raw_response:
        logger.error("No response from get_all_reports()")
        return {}
    mapping = extract_report_task_mapping(raw_response)
    if not mapping:
        logger.info("No report-task mapping found in response.")
        return {}
    save_report_task_mapping(mapping)
    return mapping

# Saving the report task mapping as a file
def save_report_task_mapping(mapping: dict) -> str:
    """
    Saves the report-task mapping to a file in REPORTS_DIR.
    The filename includes a timestamp for uniqueness.
    Returns the full path to the saved file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"report_task_mapping_{timestamp}.json"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    logger.info(f"Saved report-task mapping to {filepath}")
    return filepath

# Extracting the data and returning the mapping
def extract_report_task_mapping(raw_response: dict) -> dict:
    """
    Given the raw response dictionary from get_all_reports(),
    extract a dictionary mapping report IDs to their corresponding task IDs.
    """
    reports = raw_response.get("get_reports_response", {}).get("report", [])
    if not isinstance(reports, list):
        reports = [reports]
    
    mapping = {}
    for report in reports:
        report_id = report.get("@id")
        # The task information may be nested; adjust as needed.
        task = report.get("task", {})
        task_id = task.get("@id")
        if report_id and task_id:
            mapping[report_id] = task_id
    return mapping

###################################################################
# Functions for Loading the Mapping and Fetching Detailed Reports #           
#                                                                 #
# This section contains methods for mapping the report_id with    #
# the task_id                                                     #
###################################################################

# Function that fetches the report with the help of the task_id
def fetch_and_save_detailed_report(report_id: str) -> None:
    """
    Fetches the detailed report for the given report_id using the <get_reports> command.
    If a file for this report_id already exists in either DETAILED_REPORTS_DIR or ARCHIVE_DIR,
    it will skip fetching and saving a new report.
    """
    # Build patterns for both directories
    pattern_detailed = os.path.join(DETAILED_REPORTS_DIR, f"detailed_report_{report_id}_*.xml")
    pattern_archive = os.path.join(ARCHIVE_DIR, f"detailed_report_{report_id}_*.xml")
    
    # Check both directories for existing files
    existing_files = glob.glob(pattern_detailed) + glob.glob(pattern_archive)
    if existing_files:
        logger.info(f"Detailed report for report_id {report_id} already exists. Skipping.")
        return

    xml_command = (
        f'<get_reports report_id="{report_id}" '
        f'filter="apply_overrides=0 levels=hml min_qod=50 first=1 rows=1000 sort=name ignore_pagination=1" '
        f'details="1" format_id="a994b278-1f62-11e1-96ac-406186ea4fc5"/>'
    )
    detailed_xml = run_gvm_command(xml_command)
    if detailed_xml:
        # If detailed_xml is a dict, convert it back to an XML string.
        if isinstance(detailed_xml, dict):
            detailed_xml = xmltodict.unparse(detailed_xml, pretty=True)
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"detailed_report_{report_id}_{timestamp}.xml"
        filepath = os.path.join(DETAILED_REPORTS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(detailed_xml)
        logger.info(f"Saved detailed report for report_id {report_id} to {filepath}")
    else:
        logger.warning(f"Failed to fetch detailed report for report_id {report_id}")

# Reads the file containing the report-task mapping
def load_report_task_mapping(mapping_dir: str) -> dict:
    """
    Loads the latest report-task mapping from the specified directory.
    """
    mapping_file = get_latest_mapping_file(mapping_dir)
    if not mapping_file:
        logger.warning("No mapping file found in the directory.")
        return {}
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    return mapping

# Loads the latest mapping file 
def get_latest_mapping_file(mapping_dir: str) -> str:
    """
    Returns the latest JSON mapping file (by filename order) from the given directory.
    Assumes filenames contain a timestamp in ISO format.
    """
    files = [f for f in os.listdir(mapping_dir) if f.startswith("report_task_mapping_") and f.endswith(".json")]
    if not files:
        return None
    files.sort()  # Lexicographical sort works if timestamp is ISO formatted.
    return os.path.join(mapping_dir, files[-1])

# Helper function that processes all entries in the mapping
def process_all_detailed_reports():
    mapping = load_report_task_mapping(REPORTS_DIR)
    if not mapping:
        logger.info("No report-task mapping found.")
        return
    for report_id in mapping.keys():
        fetch_and_save_detailed_report(report_id)

# Read the XML reports and parse them to JSON 
def process_xml_reports():
    """
    For each XML file in DETAILED_REPORTS_DIR:
      - Parse the file with parse_xml_to_json()
      - Save the resulting JSON to a file in PARSED_DIR
      - Archive the processed XML file into ARCHIVE_DIR
    """
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(PARSED_DIR, exist_ok=True)

    xml_files = [f for f in os.listdir(DETAILED_REPORTS_DIR) if f.endswith(".xml")]
    if not xml_files:
        logger.info("No XML files found for processing.")
        return

    for file_name in xml_files:
        file_path = os.path.join(DETAILED_REPORTS_DIR, file_name)
        try:
            json_data = parse_xml_to_json(file_path)
            
            # Use the first vulnerability's id as the report id if available.
            vulnerabilities = json_data.get("vulnerabilities", [])
            report_id = vulnerabilities[0].get("id") if vulnerabilities else "unknown"
            vuln_count = len(vulnerabilities)
            logger.info(f"Extracted report {report_id} with {vuln_count} vulnerabilities")
            
            # Save parsed JSON file with a timestamp
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            parsed_filename = f"parsed_report_{report_id}_{timestamp}.json"
            parsed_filepath = os.path.join(PARSED_DIR, parsed_filename)
            with open(parsed_filepath, "w", encoding="utf-8") as outfile:
                json.dump(json_data, outfile, indent=2)
            logger.info(f"Saved parsed report to {parsed_filepath}")

            # Move the processed XML file to the archive directory
            shutil.move(file_path, os.path.join(ARCHIVE_DIR, file_name))
            logger.info(f"Archived file: {file_name}")
        except Exception as e:
            logger.error(f"Error processing file {file_name}: {e}")


