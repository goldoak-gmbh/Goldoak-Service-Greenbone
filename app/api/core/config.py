# app/api/core/config.py

##################################################################
# Importing packages                                             #
##################################################################

import os

##################################################################
# Required environment variables                                 #
##################################################################

def get_required_env_var(var_name):
    """Fetches a required environment variable or raises an error."""
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Missing required environment variable: {var_name}")
    return value

##################################################################
# Socket Settings for GVM                                        #
##################################################################

# Set the GVM socket path, defaulting to the expected path if not set
GVM_SOCKET_PATH = os.getenv("GVM_SOCKET_PATH", "/tmp/gvmd/gvmd/gvmd.sock")

# Credentials 
USER = os.getenv("USER", "admin")
PASSWORD = os.getenv("PASSWORD", "admin")

##################################################################
# Setting directories for workers and parser                     #
##################################################################

# Directory to store fetched reports (can be overridden via env)
REPORTS_DIR = os.getenv("REPORTS_DIR", "/app/reports")
PROCESSED_REPORTS_DIR = os.getenv("PROCESSED_REPORTS_DIR", "/app/processed_reports")
DETAILED_REPORTS_DIR = os.getenv("DETAILED_REPORTS_DIR", "/app/detailed_reports")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR", "/app/detailed_reports/archive")
PARSED_DIR = os.path.join(DETAILED_REPORTS_DIR, "parsed")

##################################################################
# Elasticsearch credentials                                      #
##################################################################

ES_HOST = get_required_env_var("ES_HOST")
ES_USER = get_required_env_var("ES_USERNAME")
ES_PASS = get_required_env_var("ES_PASSWORD")

