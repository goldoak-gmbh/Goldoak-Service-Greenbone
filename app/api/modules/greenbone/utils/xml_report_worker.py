# app/api/modules/greenbone/utils/xml_report_worker.py

##################################################################
# Importing packages                                             #
##################################################################

import os
import time
import logging
import shutil

from app.api.modules.greenbone.utils.xml_parser import parse_large_xml
#from app.api.modules.greenbone.utils.es_connector import ingest_report

##################################################################
# Environment variables and directories                          #
##################################################################

# Environment variables and directories
REPORTS_DIR = os.environ.get("DETAILED_REPORTS_DIR", "/app/detailed_reports")
ARCHIVE_DIR = os.path.join(REPORTS_DIR, "archive")
SLEEP_INTERVAL = 60  # seconds

##################################################################
# Functions                                                      #
##################################################################

def process_files():
    """
    Process each XML report file in REPORTS_DIR.
    Uses parse_large_xml() to extract data according to our detailed parsing strategy,
    ingests the data into Elasticsearch, and then moves the processed file to the archive.
    """
    for file_name in os.listdir(REPORTS_DIR):
        if file_name.endswith(".xml"):
            file_path = os.path.join(REPORTS_DIR, file_name)
            try:
                for report_json in parse_large_xml(file_path):
                    report_id = report_json.get("report_id", "unknown")
                    vulnerability_count = len(report_json.get("results", []))
                    logging.info(f"Extracted report {report_id} with {vulnerability_count} vulnerabilities")
                    
                    # Ingest the parsed report into Elasticsearch
                    #ingest_report(report_json)
                
                # Use shutil.move to handle cross-device moves
                shutil.move(file_path, os.path.join(ARCHIVE_DIR, file_name))
                logging.info(f"Processed and archived file: {file_name}")
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")

def main():
    # Ensure the archive directory exists
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    
    while True:
        process_files()
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()


