# build Python client/server
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

OUT_DIR=./python-3.10/app1_rpc
python -m grpc_tools.protoc -I./grpc --python_out=$OUT_DIR --pyi_out=$OUT_DIR --grpc_python_out=$OUT_DIR ./grpc/**/app1.proto
pushd .
cd python-3.10/app1_rpc
python setup.py sdist
popd
