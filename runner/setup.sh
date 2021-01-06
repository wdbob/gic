#/bin/bash

# install nvidia container runtime
curl -s -L https://nvidia.github.io/nvidia-docker/centos7/nvidia-docker.repo | \
tee /etc/yum.repos.d/nvidia-docker.repo && \
yum install -y nvidia-container-runtime && \
tee /etc/docker/daemon.json <<EOF
{
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF && \
systemctl daemon-reload && \
systemctl restart docker

