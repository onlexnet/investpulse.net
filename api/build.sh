# build Python client/server
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
OUT_DIR=./python-3.10
python -m grpc_tools.protoc -I./grpc --python_out=$OUT_DIR --pyi_out=$OUT_DIR --grpc_python_out=$OUT_DIR ./grpc/**/*.proto
deactivate


# build Java client/server
# cd java-21
# mvn clean install -ntp
# cd ..

