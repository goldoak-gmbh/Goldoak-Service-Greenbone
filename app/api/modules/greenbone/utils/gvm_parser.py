# app/api/modules/greenbone/utils/gvm_parser.py
##################################################################
# Importing packages                                             #
##################################################################

# General
import subprocess
import subprocess
import logging

# For parsing
import xmltodict
import json
from lxml import etree
from pydantic import BaseModel, ValidationError

# Our packages
from app.api.modules.greenbone.services import scan_service

##################################################################
# Our Parser for report overviews                                #
##################################################################

# Helper Function
def parse_report_summary(report: dict) -> dict:
    """
    Extracts a summary from a single report dictionary.
    """
    report_details = report.get("report", {})
    summary = {
        "report_id": report.get("@id"),
#        "report_name": report.get("name"),
        "scan_start": report_details.get("scan_start"),
        "scan_end": report_details.get("scan_end"),
    }

    # Extract the nested task name if available.
    task_info = report.get("task", {})
    summary["task_name"] = task_info.get("name", "N/A")
    
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


##################################################################
# Our Parser for detailed reports                                #
##################################################################
# Define a Pydantic model for report-level data
class VulnerabilityReport(BaseModel):
    report_id: str
    owner: str
    creation_time: str
    modification_time: str
    results: list  # List of vulnerability result dictionaries

def parse_large_xml(file_path: str):
    # Stream parse the XML file, looking for <report> elements
    context = etree.iterparse(file_path, events=("end",), tag="report")
    
    for event, elem in context:
        try:
            # Extract report-level metadata
            report_id = elem.get("id")
            owner = elem.findtext("owner/name")
            creation_time = elem.findtext("creation_time")
            modification_time = elem.findtext("modification_time")
            
            # Extract vulnerability results (if present)
            results = []
            results_elem = elem.find("results")
            if results_elem is not None:
                for result_elem in results_elem.findall("result"):
                    vuln = {
                        "result_id": result_elem.get("id"),
                        "name": result_elem.findtext("name"),
                        "severity": result_elem.findtext("severity"),
                        "threat": result_elem.findtext("threat"),
                        "description": result_elem.findtext("description")
                    }
                    results.append(vuln)
            
            # Prepare our report data dictionary
            report_data = {
                "report_id": report_id,
                "owner": owner,
                "creation_time": creation_time,
                "modification_time": modification_time,
                "results": results
            }
            
            # Validate and transform with Pydantic
            report_obj = VulnerabilityReport(**report_data)
            yield report_obj.dict()
        except ValidationError as ve:
            logging.error(f"Validation error in report {report_id}: {ve}")
        except Exception as e:
            logging.error(f"Error parsing report: {e}")
        finally:
            # Clear the element to free memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]