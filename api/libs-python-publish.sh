devpi use http://localhost:3141
devpi login root --password=
devpi index -c dev bases=root/pypi
devpi use dev
cd python-3.10/agent_rpc
TWINE_PASSWORD= twine upload -u root --repository-url http://localhost:3141/root/dev dist/onlexnet_app1-0.0.1.tar.gz
cd ../..
