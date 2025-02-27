# Goldoak-Service-Greenbone
## Directory structure
```bash
greenbone-automation/
├── app/
│   ├── api/                        # REST API layer (using FastAPI, Flask, etc.)
│   │   ├── routers/
│   │   │   └── scan_router.py      # Endpoints to trigger scans, get status, fetch reports
│   │   └── __init__.py
│   │
│   ├── core/                       # Core configuration, exceptions, logging, etc.
│   │   ├── config.py               # Environment variables, settings, etc.
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   ├── modules/                    # Modular integration code
│   │   ├── greenbone/              # All Greenbone-specific functionality
│   │   │   ├── api/                # If you want additional internal API code
│   │   │   │   └── __init__.py
│   │   │   ├── services/           # Business logic for scans, targets, tasks, reports
│   │   │   │   ├── scan_service.py # Create target, create task, start scan, fetch report
│   │   │   │   └── target_service.py
│   │   │   ├── utils/              # Helper functions, e.g. for parsing GMP XML
│   │   │   │   ├── gvm_parser.py   # Parse XML into JSON/dictionary
│   │   │   │   ├── socket_connector.py  # Connect to Greenbone via Unix socket (or other protocols)
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── connector/              # For integration with external systems (e.g., Elasticsearch)
│   │   │   ├── es_connector.py     # Code to push reports into Elasticsearch
│   │   │   ├── ingest_job.py       # Logic for scheduling or processing ingestion jobs
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   └── main.py                     # Entry point for the microservice application
│
├── bin/
│   └── build.sh                    # Script to build/deploy the container
│
├── Dockerfile                      # Container definition for the microservice
├── docker-compose.yml              # (Optional) for local development/testing
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Docker Compose 
**Step 1 - Preparing deployment**

```bash
sudo chown -R 1000:1000 data/
sudo chmod -R 755 data/
```

**Step 2 - Create a docker-compose.yml**

```yaml
version: "3.8"

services:
  goldoak-module-greenbone:
    image: ghcr.io/oa-goldoak/goldoak-module-greenbone:v0.4
    ports:
      - "8000:8000"
    environment:
      # This environment variable is used by your application configuration
      - GVM_SOCKET_PATH=/tmp/gvmd/gvmd/gvmd.sock
      - REPORTS_DIR=/app/reports
      - DETAILED_REPORTS_DIR=/app/detailed_reports
    volumes:
      # Mount the host directory containing the Unix socket.
      # Adjust the host path as needed.
      - /tmp/gvm/gvmd:/tmp/gvmd/gvmd:ro
      - /home/azureuser/Goldoak-Service-Greenbone/data/report_ids:/app/reports:rw
      - /home/azureuser/Goldoak-Service-Greenbone/data/reports:/app/detailed_reports:rw
    user: "1000:1000"  # Run as non-root user
```

