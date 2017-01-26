import airflow.hooks
from airflow.operators.docker_operator import DockerOperator
import airflow.models
import os


def get_postgres_uri(name):
    conn = airflow.hooks.BaseHook.get_connection(name)
    if not conn:
        return

    uri = 'postgres://{user}:{password}@{host}:{port}/{schema}'
    return uri.format(
        user=conn.login,
        password=conn.password,
        host=conn.host,
        port=conn.port or 5432,
        schema=conn.schema
    )


def create_collector_task(name, dag, command=None, environment=None):
    default_command = 'make start {}'.format(name)

    return _create_task(
        task_id='collector_{}'.format(name),
        dag=dag,
        image='okibot/collectors:latest',
        command=command or default_command,
        environment=environment or {},
    )


def create_processor_task(name, dag, command=None, environment=None):
    default_command = 'make start {}'.format(name)

    return _create_task(
        task_id='processor_{}'.format(name),
        dag=dag,
        image='okibot/processors:latest',
        command=command or default_command,
        environment=environment or {},
    )


def _create_task(task_id, dag, image, command, environment):
    env = {
        'WAREHOUSE_URL': get_postgres_uri('warehouse_db'),
        'DATABASE_URL': get_postgres_uri('api_db'),
        'EXPLORERDB_URL': get_postgres_uri('explorer_db'),
        'PYTHON_ENV': airflow.models.Variable.get('ENV'),
        'LOGGING_URL': airflow.models.Variable.get('LOGGING_URL'),
        'DOWNLOAD_DELAY': airflow.models.Variable.get('DOWNLOAD_DELAY'),
    }
    env.update(environment)
    docker_api_version = os.environ.get('DOCKER_API_VERSION', '1.23')

    return DockerOperator(
        task_id=task_id,
        dag=dag,
        image=image,
        command=command,
        environment=env,
        api_version=docker_api_version,
        force_pull=True,
    )
