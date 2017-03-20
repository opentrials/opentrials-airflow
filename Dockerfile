# AUTHOR: Roberto Vitillo
# DESCRIPTION: Mozilla's Airflow container
# BUILD: docker build --rm -t opentrials/opentrials-airflow
# SOURCE: https://github.com/opentrials/opentrials-airflow

FROM puckel/docker-airflow:1.7.1.3-7
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

ADD ansible/files/airflow/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
ADD ansible/files/airflow/runner.sh ${AIRFLOW_HOME}/runner.sh
ADD ansible/files/airflow/replace_env.py ${AIRFLOW_HOME}/replace_env.py
ADD ansible/files/airflow/entrypoint.sh /entrypoint.sh
RUN chown airflow:airflow ${AIRFLOW_HOME}/airflow.cfg

ENV AIRFLOW_USER airflow

ADD dags/ /usr/local/airflow/dags/
