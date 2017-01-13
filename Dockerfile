# AUTHOR: Roberto Vitillo
# DESCRIPTION: Mozilla's Airflow container
# BUILD: docker build --rm -t okibot/opentrials-airflow
# SOURCE: https://github.com/opentrials/opentrials-airflow

FROM puckel/docker-airflow:1.7.1.3
MAINTAINER okibot

USER root
RUN apt-get update -yqq && \
    apt-get install -yqq python-pip

ADD requirements.txt /
RUN pip install -r /requirements.txt

ADD ansible/files/airflow/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
ADD ansible/files/airflow/entrypoint.sh ${AIRFLOW_HOME}/entrypoint.sh
ADD ansible/files/airflow/runner.sh ${AIRFLOW_HOME}/runner.sh
ADD ansible/files/airflow/replace_env.py ${AIRFLOW_HOME}/replace_env.py
RUN chown airflow:airflow ${AIRFLOW_HOME}/airflow.cfg

ENV AIRFLOW_USER airflow

ADD dags/ /usr/local/airflow/dags/
