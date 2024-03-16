python ./utils/serialize_grpc.py agent_rpc
python ./utils/serialize_avro.py agent_rpc

python ./utils/serialize_grpc.py app1_rpc
python ./utils/serialize_avro.py app1_rpc

python ./utils/serialize_grpc.py market_rpc
python ./utils/serialize_avro.py market_rpc

python ./utils/serialize_grpc.py scheduler_rpc
python ./utils/serialize_avro.py scheduler_rpc

# _PYTHON_LIBS_DIR=./python
# _SCHEMA_DIR=./schema
# _PROJECT_DIR=app1_rpc

# _CODEGEN_ROOT_DIR=$_PYTHON_LIBS_DIR/$_PROJECT_DIR/$_PROJECT_DIR
# _PROJECT_SCHEMA_DIR=$_SCHEMA_DIR/$_PROJECT_DIR

# mkdir -p $_CODEGEN_ROOT_DIR
# touch $_CODEGEN_ROOT_DIR/__init__.py

# Generate ABRO
# generate initial output folder, it will contains __init__.py thanks to avro codegen
# rm -s python-3.11/market_rpc/dist/*
# python serialize_avro.py "$_PROJECT_SCHEMA_DIR/schema.avsc" $_CODEGEN_ROOT_DIR

# Generate GRPC
# python -m grpc_tools.protoc --proto_path=$_PROJECT_SCHEMA_DIR --python_out=$_CODEGEN_ROOT_DIR --pyi_out=$_CODEGEN_ROOT_DIR --grpc_python_out=$_CODEGEN_ROOT_DIR $_PROJECT_SCHEMA_DIR/*.proto
# pushd .
# cd python-3.11/app1_rpc
# python setup.py sdist
# popd

# # generate initial folder with __init__.py thanks to avro codegen
# rm -s python-3.11/market_rpc/dist/*
# python serialize_avro.py "./grpc/market_rpc/schema.avsc" python-3.11/market_rpc/market_rpc
# # ... and proto part as well
# OUT_DIR=./python-3.11/market_rpc
# python -m grpc_tools.protoc -I./grpc --python_out=$OUT_DIR --pyi_out=$OUT_DIR --grpc_python_out=$OUT_DIR ./grpc/market_rpc/*.proto
# pushd .
# cd python-3.11/market_rpc
# python setup.py sdist
# popd

