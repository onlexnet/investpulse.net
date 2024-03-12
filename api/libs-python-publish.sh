devpi use http://localhost:3141
devpi login root --password=
devpi index -c dev bases=root/pypi
devpi use root/dev
TWINE_PASSWORD= twine upload -u root --repository-url http://localhost:3141/root/dev python-3.10/app1_rpc/dist/*
