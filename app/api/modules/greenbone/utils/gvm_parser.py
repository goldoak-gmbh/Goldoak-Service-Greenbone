# app/api/modules/greenbone/utils/gvm_parser.py

##################################################################
# Importing packages                                             #
##################################################################

# General
import os
import time
import shutil
import subprocess
import logging

# For parsing
import xmltodict
import json
from lxml import etree
from typing import Optional, List, Dict
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
#        "report_name": report.get("name"), # Not needed anymore
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
    owner: Optional[str] = ""         # Allow missing owner
    creation_time: Optional[str] = ""   # Allow missing creation time
    modification_time: Optional[str] = ""  # Allow missing modification time
    results: List[Dict] = []

def parse_xml_to_json(xml_file_path: str) -> dict:
    """
    Parses the provided XML file and extracts vulnerability result data.
    Returns a dictionary with a single key "vulnerabilities" that holds a list of extracted results.
    """
    tree = etree.parse(xml_file_path)
    root = tree.getroot()

    # Use an XPath expression to locate all <result> elements nested under <report>/<results>
    result_elements = root.xpath(".//report/results/result")
    
    vulnerabilities = []
    for result in result_elements:
        vuln = {}
        # Basic fields
        vuln["id"] = result.get("id")
        vuln["title"] = result.findtext("name")
        vuln["creation_time"] = result.findtext("creation_time")
        vuln["modification_time"] = result.findtext("modification_time")
        
        # Process host info
        host_elem = result.find("host")
        host_info = {}
        if host_elem is not None:
            host_info["hostname"] = host_elem.findtext("hostname")
            # Sometimes the IP appears as tail text after the hostname element
            hostname_elem = host_elem.find("hostname")
            if hostname_elem is not None and hostname_elem.tail:
                host_info["ip"] = hostname_elem.tail.strip()
        vuln["host"] = host_info

        # Port info
        vuln["port"] = result.findtext("port")
        
        # Extract details from <nvt>
        nvt_elem = result.find("nvt")
        nvt_info = {}
        if nvt_elem is not None:
            nvt_info["type"] = nvt_elem.findtext("type")
            nvt_info["name"] = nvt_elem.findtext("name")
            nvt_info["family"] = nvt_elem.findtext("family")
            nvt_info["cvss_base"] = nvt_elem.findtext("cvss_base")
            nvt_info["tags"] = nvt_elem.findtext("tags")
            nvt_info["solution"] = nvt_elem.findtext("solution")
            # Grab one severity detail if available
            severity_elem = nvt_elem.find(".//severity")
            if severity_elem is not None:
                nvt_info["severity_score"] = severity_elem.findtext("score")
                nvt_info["severity_value"] = severity_elem.findtext("value")
        vuln["nvt"] = nvt_info

        vuln["threat"] = result.findtext("threat")
        vuln["severity"] = result.findtext("severity")
        vuln["qod"] = result.findtext("qod/value")
        vuln["description"] = result.findtext("description")

        vulnerabilities.append(vuln)

    return {"vulnerabilities": vulnerabilities}



