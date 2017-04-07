# AUTHOR: Roberto Vitillo
# DESCRIPTION: Mozilla's Airflow container
# BUILD: docker build --rm -t opentrials/opentrials-airflow
# SOURCE: https://github.com/opentrials/opentrials-airflow

FROM puckel/docker-airflow:1.8.0
MAINTAINER opentrials

USER root
RUN apt-get update -yqq && \
    apt-get install -yqq \
        sudo \
        python-pip \
        postgresql-client \
        git

ADD requirements.txt /
RUN pip uninstall airflow -y && \
    pip install -r /requirements.txt

ARG AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_HOME ${AIRFLOW_HOME}
ENV AIRFLOW_USER airflow

ADD ansible/files/airflow/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
ADD ansible/files/airflow/runner.sh ${AIRFLOW_HOME}/runner.sh
ADD ansible/files/airflow/replace_env.py ${AIRFLOW_HOME}/replace_env.py
ADD ansible/files/airflow/entrypoint.sh /entrypoint.sh
RUN chown ${AIRFLOW_USER}:${AIRFLOW_USER} ${AIRFLOW_HOME}/airflow.cfg

ADD dags/ ${AIRFLOW_HOME}/dags/
