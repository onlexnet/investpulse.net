FROM ubuntu:22.04
RUN apt update && apt upgrade -y && apt install -y \
    openssh-client \
    sudo \
    # require graphviz to run PlantUML vscode plugin
    # more: https://plantuml.com/graphviz-dot
    graphviz \
    curl


# Let use some unsername instead of default root
RUN useradd -ms /bin/bash worker

#  Add new user worker to sudo group
RUN adduser worker sudo

# Ensure sudo group users are not 
# asked for a password when using 
# sudo command by ammending sudoers file
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# install skaffold
RUN curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/v2.14.1/skaffold-linux-amd64 && install skaffold /usr/local/bin/

# install ip required by 'minikube tunnel' command
RUN sudo apt update && sudo apt install iproute2 -y

# Switch to the worker user
USER worker
