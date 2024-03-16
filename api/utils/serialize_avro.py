import logging
import os
import sys
from avrogen import write_schema_files
from pathlib import Path

PROJECT_DIR = sys.argv[1] # e.g. app1_rpc, name of subfolder in schema directory

CURRENT_DIR=os.getcwd()
PYTHON_LIBS_DIR=f"{CURRENT_DIR}/python"
SCHEMA_DIR=f"{CURRENT_DIR}/schema"
PROJECT_SCHEMA_DIR=f"{SCHEMA_DIR}/{PROJECT_DIR}"
MAYBE_SCHEMA_FILE=f"{PROJECT_SCHEMA_DIR}/schema.avsc"
CODEGEN_ROOT_DIR=f"{PYTHON_LIBS_DIR}/{PROJECT_DIR}"

if (Path(MAYBE_SCHEMA_FILE).exists()):
    SCHEMA_FILE = MAYBE_SCHEMA_FILE
    schema_json = Path(SCHEMA_FILE).read_text()
    write_schema_files(schema_json, CODEGEN_ROOT_DIR)
else:
    logging.warning(f"AVRO file does not exists: {MAYBE_SCHEMA_FILE}")
