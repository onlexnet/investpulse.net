devpi use http://localhost:3141
devpi login root --password=
devpi index -c dev bases=root/pypi
devpi use root/dev
export TWINE_PASSWORD=
twine upload -u root --repository-url http://localhost:3141/root/dev python-3.11/app1_rpc/dist/*
twine upload -u root --repository-url http://localhost:3141/root/dev python-3.11/market_rpc/dist/*
