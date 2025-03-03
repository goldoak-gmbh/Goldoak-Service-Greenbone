# app/api/modules/greenbone/utils/es_ingest.py

##################################################################
# Importing packages                                             #
##################################################################

import os
import json
import glob
import logging
from elasticsearch import Elasticsearch

from app.api.core.config import ES_HOST, ES_USER, ES_PASS, PARSED_DIR

##################################################################
# Defining our logger                                            #
##################################################################

logger = logging.getLogger(__name__)

##################################################################
# Defining the ingest                                            #
##################################################################

def ingest_parsed_reports():
    """
    Scans the PARSED_DIR for JSON report files. For each file that hasn't been ingested,
    it indexes each vulnerability document into Elasticsearch and then marks the file as ingested.
    """
    # Connect to Elasticsearch
    print(ES_HOST)
    logger.info(f"Connecting to: '{ES_HOST}'")
    es = Elasticsearch(ES_HOST, http_auth=(ES_USER, ES_PASS))
    
    # Define your index name and mapping
    index_name = "goldoak_vulnerabilities"
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text"},
                "creation_time": {"type": "date"},
                "modification_time": {"type": "date"},
                "host": {
                    "properties": {
                        "hostname": {"type": "keyword"},
                        "ip": {"type": "ip"}
                    }
                },
                "port": {"type": "keyword"},
                "nvt": {
                    "properties": {
                        "type": {"type": "keyword"},
                        "name": {"type": "text"},
                        "family": {"type": "keyword"},
                        "cvss_base": {"type": "float"},
                        "tags": {"type": "text"},
                        "solution": {"type": "text"},
                        "severity_score": {"type": "float"},
                        "severity_value": {"type": "keyword"}
                    }
                },
                "threat": {"type": "keyword"},
                "severity": {"type": "float"},
                "qod": {"type": "integer"},
                "description": {"type": "text"}
            }
        }
    }
    
    # Create the index if it doesn't exist
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)
        logger.info(f"Index '{index_name}' created.")

    # Determine the path for the ingested reports record file
    ingested_file_path = os.path.join(PARSED_DIR, "ingested_reports.txt")
    if os.path.exists(ingested_file_path):
        with open(ingested_file_path, "r") as f:
            ingested_reports = set(line.strip() for line in f if line.strip())
    else:
        ingested_reports = set()

    # List all JSON files in PARSED_DIR
    json_files = glob.glob(os.path.join(PARSED_DIR, "*.json"))
    logger.info(f"Found {len(json_files)} parsed report files in '{PARSED_DIR}'.")

    for json_file in json_files:
        filename = os.path.basename(json_file)
        if filename in ingested_reports:
            logger.info(f"Skipping already ingested file: {filename}")
            continue

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {filename}: {e}")
            continue

        vulnerabilities = data.get("vulnerabilities", [])
        for vulnerability in vulnerabilities:
            doc_id = vulnerability.get("id")
            if not doc_id:
                logger.warning(f"Skipping vulnerability with missing id in file {filename}")
                continue
            try:
                res = es.index(index=index_name, id=doc_id, body=vulnerability)
                logger.info(f"Indexed vulnerability {doc_id} from {filename}: {res.get('result')}")
            except Exception as e:
                logger.error(f"Error indexing vulnerability {doc_id} from {filename}: {e}")

        # Mark file as ingested
        ingested_reports.add(filename)
        logger.info(f"File {filename} ingested.")

    # Save the updated list of ingested files
    try:
        with open(ingested_file_path, "w", encoding="utf-8") as f:
            for fname in sorted(ingested_reports):
                f.write(fname + "\n")
        logger.info("Updated ingested reports list.")
    except Exception as e:
        logger.error(f"Error saving ingested reports list: {e}")


