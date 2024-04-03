(SERVICE_NAME=onlexnet; cd ./python/$SERVICE_NAME; rm -rf dist; python setup.py sdist)

(SERVICE_NAME=agent_rpc; cd ./python/$SERVICE_NAME; rm -rf dist; python setup.py sdist)

(SERVICE_NAME=app1_rpc; cd ./python/$SERVICE_NAME; rm -rf dist; python setup.py sdist)

(SERVICE_NAME=market_rpc; cd ./python/$SERVICE_NAME; rm -rf dist; python setup.py sdist)

(SERVICE_NAME=scheduler_rpc; cd ./python/$SERVICE_NAME; rm -rf dist; python setup.py sdist)

(SERVICE_NAME=signals_rpc; cd ./python/$SERVICE_NAME; rm -rf dist; python setup.py sdist)
