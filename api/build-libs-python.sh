# build Python client/server
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
OUT_DIR=./python-3.10
python -m grpc_tools.protoc -I./grpc --python_out=$OUT_DIR --pyi_out=$OUT_DIR --grpc_python_out=$OUT_DIR ./grpc/**/*.proto
cd python-3.10/agent_rpc
python setup.py sdist

devpi use http://localhost:3141
devpi login root --password=
devpi index -c dev bases=root/pypi
devpi use root/dev
TWINE_PASSWORD= twine upload -u root --repository-url http://localhost:3141/root/dev dist/verysimplemodule-0.0.1.tar.gz

deactivate
