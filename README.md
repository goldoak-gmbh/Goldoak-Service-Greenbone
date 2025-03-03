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

---

## GVM-CLI 
### Getting Scan Configs 
```bash
gvm-cli --gmp-username admin --gmp-password admin socket --socketpath /tmp/gvm/gvmd/gvmd.sock --pretty --xml "<get_configs/>"
```

### Available Scan Configs
| Name | Description | Scan ID |
| ----------- | ----------- | ----------- |
| Base | Basic configuration template with a minimum set of NVTs required for a scan. Version 20200827. | `d21f6c81-2b88-4ac1-b7b4-a2a9f2ad4663` |
| Discovery | Network Discovery scan configuration. Version 20201215. | `8715c877-47a0-438d-98a3-27c7a6ab2196` |
| Base | Empty and static configuration template. Version 20201215. | `085569ce-73ed-11df-83c3-002264764cea` |
| EulerOS Linux Security Configuration | Check compliance status of EulerOS 2.0 SP3/SP5/SP8 installation against above named Policy as distributed by Huawei. Version 20201215. | `0362e8f6-d7cc-4a12-8768-5f2406713860` |
| Full and fast | Most NVT's; optimized by using previously collected information. Version 20201215. | `daba56c8-73ec-11df-a475-002264764cea` |
| GaussDB 100 V300R001C00 Security Hardening Guide (Standalone) | Check compliance status of GaussDB installation against above named Policy as distributed by Huawei (based on Issue 5). Version 20201215. | `61327f09-8a54-4854-9e1c-16798285fb28` |
| GaussDB Kernel V500R001C00 Security Hardening Guide | Check compliance status againt mentioned policy (based on Issue 01 from 2020-07-21). Version 20201222. | `2eec8313-fee4-442a-b3c4-fa0d5dc83d61` |
| Host Discovery | | `2d3f051c-55ba-11e3-bf43-406186ea4fc5` |
| Huawei Datacom Product Security Configuration Audit Guide | Check compliance status of Huawei Datacom Device against above named Policy as distributed by Huawei. Version 20211209. | `aab5c4a1-eab1-4f4e-acac-8c36d08de6bc` |
| IT-Grundschutz Kompendium | Policy f&#252;r Bausteine: SYS 1.2.2, SYS 2.2.2, SYS 2.2.3, SYS 1.3, SYS 2.3. Version 20210318. | `c4b7c0cb-6502-4809-b034-8e635311b3e6` |




