# app/api/modules/greenbone/services/scan_service.py

##################################################################
# Importing packages                                             #
##################################################################
import subprocess
import xmltodict
import logging


##################################################################
# Create a Logger                                                #
##################################################################

# Configure a logger for debugging purposes
logger = logging.getLogger(__name__)


##################################################################
# Establish connection with Greenbone                            #
##################################################################

# Adjust the socket path as needed (e.g., via configuration)
SOCKET_PATH = "/tmp/gvm/gvmd/gvmd.sock"


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
            "--gmp-username", "admin",
            "--gmp-password", "admin",
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