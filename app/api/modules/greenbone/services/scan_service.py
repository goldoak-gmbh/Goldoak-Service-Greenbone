# app/api/modules/greenbone/services/scan_service.py

##################################################################
# Importing packages                                             #
##################################################################
import subprocess
import xmltodict
import subprocess
import logging

from app.api.core.config import (
    GVM_SOCKET_PATH,
    USER,
    PASSWORD
)

##################################################################
# Create a Logger                                                #
##################################################################

# Configure a logger for debugging purposes
logger = logging.getLogger(__name__)


##################################################################
# Establish connection with Greenbone                            #
##################################################################

# Adjust the socket path as needed (e.g., via configuration)
SOCKET_PATH = GVM_SOCKET_PATH


##################################################################
# Define functions for communication                             #
##################################################################

# Main function to run gvm commands
def run_gvm_command(xml_command: str) -> dict:
    """
    Executes a gvm-cli command using the Unix socket and returns the parsed XML response.
    """
    try:
        cmd = [
            "gvm-cli",
            "--gmp-username", USER,
            "--gmp-password", PASSWORD,
            "socket",
            "--socketpath", SOCKET_PATH,
            "--xml", xml_command
        ]
        logger.debug(f"Running command: {' '.join(cmd)}")
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        # Parse the XML output into a dictionary for easy processing.
        result = xmltodict.parse(output)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running gvm-cli command: {e.output.decode()}")
        raise

# Retrieve version information of Greenbone via gvm
def get_version() -> dict:
    """
    Retrieves the GVM version.
    """
    xml = "<get_version/>"
    return run_gvm_command(xml)

def get_all_reports() -> dict:
    xml = "<get_reports/>"
    response = run_gvm_command(xml)
    return response  # then extract report IDs as needed


def create_target(name: str, hosts: str) -> str:
    """
    Creates a new target and returns its ID.
    """
    xml = (
        f"<create_target>"
        f"<name>{name}</name>"
        f"<hosts>{hosts}</hosts>"
        f"<port_list id='33d0cd82-57c6-11e1-8ed1-406186ea4fc5'/>" # Default port range. Need to make it variable later
        f"</create_target>"
    )
    response = run_gvm_command(xml)
    # Parse the target id from the response.
    target_id = response.get("create_target_response", {}).get("@id")
    return target_id

def create_task(name: str, target_id: str, scan_config_id: str) -> str:
    """
    Creates a scan task for the given target and configuration.
    Returns the task ID.
    """
    xml = (
        f"<create_task>"
        f"<name>{name}</name>"
        f"<config id='{scan_config_id}'/>"
        f"<target id='{target_id}'/>"
        f"</create_task>"
    )
    response = run_gvm_command(xml)
    task_id = response.get("create_task_response", {}).get("@id")
    return task_id

def start_task(task_id: str) -> None:
    """
    Starts a scan task given its ID.
    """
    xml = f"<start_task task_id='{task_id}'/>"
    run_gvm_command(xml)

def get_report(report_id: str) -> dict:
    """
    Retrieves the report details.
    """
    xml = f"<get_report report_id='{report_id}' details='1'/>"
    response = run_gvm_command(xml)
    return response