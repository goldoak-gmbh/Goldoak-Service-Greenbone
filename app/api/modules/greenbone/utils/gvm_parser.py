# app/api/modules/greenbone/utils/gvm_parser.py
##################################################################
# Importing packages                                             #
##################################################################

import subprocess
import xmltodict
import subprocess
import logging

from app.api.modules.greenbone.services import scan_service

##################################################################
# Our Parsers                                                    #
##################################################################

# Helper Function
def parse_report_summary(report: dict) -> dict:
    """
    Extracts a summary from a single report dictionary.
    """
    report_details = report.get("report", {})
    summary = {
        "report_id": report.get("@id"),
        "report_name": report.get("name"),
        "scan_start": report_details.get("scan_start"),
        "scan_end": report_details.get("scan_end"),
    }
    # Extract vulnerability count from 'vulns' if available
    vulns = report_details.get("vulns", {})
    summary["vuln_count"] = vulns.get("count")
    
    # Optionally, extract a breakdown from the result_count section:
    result_count = report_details.get("result_count", {})
    if result_count:
        # Remove any additional text if necessary; you can refine this as needed.
        summary["result_count"] = {
            "full": result_count.get("full"),
            "filtered": result_count.get("filtered")
        }
    
    return summary

# Actual function to parse all reports and return them 
def parse_all_reports(reports_response: dict) -> list:
    """
    Given the parsed XML response from <get_reports/>, extract summaries for each report.
    """
    reports = reports_response.get("get_reports_response", {}).get("report", [])
    # Ensure reports is always a list
    if not isinstance(reports, list):
        reports = [reports]
    return [parse_report_summary(report) for report in reports]

