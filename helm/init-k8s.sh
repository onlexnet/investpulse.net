# Scripts allows quickly define handful aliases for kubectl and helm
# Example usage: . init-k8s.sh onlexnet-ptn-dev
# so later on you may use aliases
# k == kubectl --namespace onlexnet-ptn-dev
# h == helm --namespace onlexnet-ptn-dev
# where ptn means: predectivetrading.net
namespace="onlexnet-ptn-$1"
alias kc="kubectl"
alias k="kc --namespace $namespace"
alias h="helm --namespace $namespace"

# examples how to use aliases:
# install application -> h install pdn ./main/