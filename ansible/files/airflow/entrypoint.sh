#!/usr/bin/env bash

# Create Docker group to be able to access /var/run/docker.sock
DOCKER_SOCKET=/var/run/docker.sock
DOCKER_GROUP=docker

if [ -S ${DOCKER_SOCKET} ]; then
    DOCKER_GID=$(stat -c '%g' ${DOCKER_SOCKET})
    groupadd -for -g ${DOCKER_GID} ${DOCKER_GROUP}
    usermod -aG ${DOCKER_GROUP} ${AIRFLOW_USER}
    echo "Created group '${DOCKER_GROUP}' (GID ${DOCKER_GID}) and added '${AIRFLOW_USER}' to it."
fi

# Switch to a non-root user and continue
sudo -E -H -u ${AIRFLOW_USER} -- /usr/bin/env bash $AIRFLOW_HOME/runner.sh ${@}
