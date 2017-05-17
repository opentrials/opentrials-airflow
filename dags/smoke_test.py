# Smoke test to make sure we can run Docker containers
import os
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.docker_operator import DockerOperator
from operators.docker_cli_operator import DockerCLIOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2017, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    dag_id='smoke_test',
    default_args=default_args,
    max_active_runs=1,
    schedule_interval='@daily'
)

sleep_task = DockerOperator(
    task_id='sleep',
    dag=dag,
    image='alpine:latest',
    api_version=os.environ.get('DOCKER_API_VERSION', '1.23'),
    command='sleep 5'
)

docker_cli_sleep_task = DockerCLIOperator(
    task_id='docker_cli_sleep',
    dag=dag,
    image='alpine:latest',
    command='sleep 5'
)
