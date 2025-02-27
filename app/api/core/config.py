# app/api/core/config.py
import os

# Set the GVM socket path, defaulting to the expected path if not set
GVM_SOCKET_PATH = os.getenv("GVM_SOCKET_PATH", "/tmp/gvmd/gvmd/gvmd.sock")

# Directory to store fetched reports (can be overridden via env)
REPORTS_DIR = os.getenv("REPORTS_DIR", "/app/reports")
PROCESSED_REPORTS_DIR = os.getenv("PROCESSED_REPORTS_DIR", "/app/processed_reports")
DETAILED_REPORTS_DIR = os.getenv("DETAILED_REPORTS_DIR", "/app/detailed_reports")

# Credentials 
USER = os.getenv("USER", "admin")
PASSWORD = os.getenv("PASSWORD", "admin")
