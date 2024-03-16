from pathlib import Path
import sys
from grpc_tools import protoc
import os

PROJECT_DIR = sys.argv[1] # e.g. app1_rpc, name of subfolder in schema directory

CURRENT_DIR=os.getcwd()
PYTHON_LIBS_DIR=f"{CURRENT_DIR}/python"
SCHEMA_DIR=f"{CURRENT_DIR}/schema"

CODEGEN_ROOT_DIR=f"{PYTHON_LIBS_DIR}/{PROJECT_DIR}/{PROJECT_DIR}"
PROJECT_SCHEMA_DIR=f"{SCHEMA_DIR}/{PROJECT_DIR}"


schema_file = f"{PROJECT_SCHEMA_DIR}/schema.proto"
if (Path(schema_file).exists()):
    Path(CODEGEN_ROOT_DIR).mkdir(parents=True, exist_ok=True)
    open(f"{CODEGEN_ROOT_DIR}/__init__.py", 'a').close()

    # Generate GRPC
    protoc.main([
        f"ignored", # the first argument is often considered as the name of the program being run (based on ChatGPT hint)
        f"--proto_path={PROJECT_SCHEMA_DIR}",
        f"--python_out={CODEGEN_ROOT_DIR}",
        f"--pyi_out={CODEGEN_ROOT_DIR}",
        f"--grpc_python_out={CODEGEN_ROOT_DIR}",
        schema_file])
