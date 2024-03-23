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

import fileinput

def replace_import(filename, old_line, new_line):
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            if line.strip() == old_line:
                print(new_line)
            else:
                print(line, end='')


# workaround for
# https://github.com/grpc/grpc/issues/9575#issuecomment-293934506
replace_import(f'{CODEGEN_ROOT_DIR}/schema_pb2_grpc.py', 'import schema_pb2 as schema__pb2', 'from . import schema_pb2 as schema__pb2')