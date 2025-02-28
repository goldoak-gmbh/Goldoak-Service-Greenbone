import os
import time
import logging
from app.api.modules.greenbone.utils.gvm_parser import parse_large_xml
from app.api.modules.greenbone.utils.es_connector import ingest_report

# Use the DETAILED_REPORTS_DIR environment variable, defaulting to /app/detailed_reports
REPORTS_DIR = os.environ.get("DETAILED_REPORTS_DIR", "/app/detailed_reports")
ARCHIVE_DIR = os.path.join(REPORTS_DIR, "archive")
SLEEP_INTERVAL = 60  # seconds

def process_files():
    """
    Process each XML report file in the REPORTS_DIR.
    
    Parsing strategy:
      - Report-Level Metadata:
         * Extract attributes such as id, format_id, config_id, extension, content_type.
         * Owner (from <owner>/<name>) and report identifier (<name>).
         * Timestamps like <creation_time>, <modification_time>, nested <timestamp>, and <scan_start>.
         * Task details (including nested target info) and report format.
      
      - Scan and Summary Data:
         * Scan run status (<scan_run_status>).
         * Counts for hosts, vulns, os, apps, ssl_certs and detailed breakdown in <result_count>.
      
      - Environment & Configuration:
         * Filters and sorting information (<filters> with <term>, <filter>, <keywords>).
         * Time zone details (<timezone>, <timezone_abbrev>).
      
      - Port Data:
         * For each <port>: extract host, port identifier (e.g., “general/tcp” or “22/tcp”), severity, and threat.
      
      - Vulnerability Results:
         * For each <result> under <results>:
             - Identification & Timing: id, name, creation/modification times.
             - Detection details: nested <detection> information.
             - Host info: asset, hostname, and IP.
             - Port info.
             - Vulnerability specifics from the <nvt> block (oid, type, name, family, cvss_base, severities, tags, solution, refs).
             - Risk assessment: threat, severity, qod, description, original_threat, original_severity, compliance.
    """
    for file_name in os.listdir(REPORTS_DIR):
        if file_name.endswith(".xml"):
            file_path = os.path.join(REPORTS_DIR, file_name)
            try:
                # Use the comprehensive parser to extract detailed report data.
                for report_json in parse_large_xml(file_path):
                    # For debugging, log key extracted fields
                    report_id = report_json.get("report_id", "unknown")
                    vulnerability_count = len(report_json.get("results", []))
                    logging.info(f"Extracted report {report_id} with {vulnerability_count} vulnerabilities")
                    
                    # Ingest the report JSON into Elasticsearch.
                    # ingest_report(report_json)
                
                # Move the processed file to the archive directory to prevent reprocessing.
                os.rename(file_path, os.path.join(ARCHIVE_DIR, file_name))
                logging.info(f"Processed and archived file: {file_name}")
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")

def main():
    # Ensure the archive directory exists.
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    
    # Continuously check for new XML files at defined intervals.
    while True:
        process_files()
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
