set -e

# Function to get minikube IP and handle errors
check_minikube_working() {
    local ip
    if ! ip=$(minikube ip 2>/dev/null); then
        echo "Error: Minikube is not running or an error occurred." >&2
        exit 1
    fi
    echo "Minikube IP: $ip"
}

export MINIKUBE_IP=$(minikube ip)
# Append the new DNS server to resolv.conf as the first resolver (when is the secnod one, it does not resolve ingres entries)
sudo cp /etc/hosts /tmp/hosts
echo "$MINIKUBE_IP nexus.local" | cat - /tmp/hosts | sudo tee /etc/hosts > /dev/null
