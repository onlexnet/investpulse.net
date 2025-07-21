# build Python client/server

OUT_DIR=./python-3.11/app1_rpc
python -m grpc_tools.protoc -I./grpc --python_out=$OUT_DIR --pyi_out=$OUT_DIR --grpc_python_out=$OUT_DIR ./grpc/app1_rpc/*.proto
pushd .
cd python-3.11/app1_rpc
python setup.py sdist
popd

# generate initial folder with __init__.py thanks to avro codegen
rm -s python-3.11/market_rpc/dist/*
python serialize_avro.py "./grpc/market_rpc/schema.avsc" python-3.11/market_rpc/market_rpc
# ... and proto part as well
OUT_DIR=./python-3.11/market_rpc
python -m grpc_tools.protoc -I./grpc --python_out=$OUT_DIR --pyi_out=$OUT_DIR --grpc_python_out=$OUT_DIR ./grpc/market_rpc/*.proto
pushd .
cd python-3.11/market_rpc
python setup.py sdist
popd

