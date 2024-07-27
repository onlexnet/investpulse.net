# Dev notes
Install/upgrade
```bash
helm upgrade --install onlexnet-infra-dev . -f values.yaml --create-namespace --namespace onlexnet-infra-dev
```


# nexus
# https://artifacthub.io/packages/helm/stevehipwell/nexus3
helm repo add stevehipwell https://stevehipwell.github.io/helm-charts/
helm pull stevehipwell/nexus3

# Install / upgrade
# note - should be invoked inside infra-dev
helm upgrade --install dev-services . --namespace onlexnet-infra-dev --values ./values.yaml --create-namespace
