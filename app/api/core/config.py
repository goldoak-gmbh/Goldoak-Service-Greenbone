# app/api/core/config.py

##################################################################
# Importing packages                                             #
##################################################################

import os

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




