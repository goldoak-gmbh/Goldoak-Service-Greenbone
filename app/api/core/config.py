# app/api/core/config.py
import os

# Set the GVM socket path, defaulting to the expected path if not set
GVM_SOCKET_PATH = os.getenv("GVM_SOCKET_PATH", "/tmp/gvmd/gvmd/gvmd.sock")


# You can add more configuration variables here as needed

