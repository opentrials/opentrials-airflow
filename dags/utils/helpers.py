import airflow.hooks.base_hook
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
import airflow.models
import os


def get_postgres_uri(name):
    conn = airflow.hooks.base_hook.BaseHook.get_connection(name)
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


def create_trigger_subdag_task(trigger_dag_id, dag):
    def _always_trigger(context, dag_run_obj):
        return dag_run_obj

    return TriggerDagRunOperator(
        task_id='trigger_{trigger}_from_{dag}'.format(
            trigger=trigger_dag_id,
            dag=dag.dag_id
        ),
        dag=dag,
        trigger_dag_id=trigger_dag_id,
        python_callable=_always_trigger
    )


def create_collector_task(name, dag, command=None, environment=None):
    default_command = 'make start {}'.format(name)
    env = {
        'SENTRY_DSN': airflow.models.Variable.get('COLLECTOR_SENTRY_DSN'),
    }
    env.update(environment or {})

    return _create_task(
        task_id='collector_{}'.format(name),
        dag=dag,
        image='opentrials/collectors:latest',
        command=command or default_command,
        environment=env,
    )


def create_processor_task(name, dag, command=None, environment=None):
    default_command = 'make start {}'.format(name)
    env = {
        'SENTRY_DSN': airflow.models.Variable.get('PROCESSOR_SENTRY_DSN'),
    }
    env.update(environment or {})

    return _create_task(
        task_id='processor_{}'.format(name),
        dag=dag,
        image='opentrials/processors:latest',
        command=command or default_command,
        environment=env,
    )


def _create_task(task_id, dag, image, command, environment):
    env = {
        'WAREHOUSE_URL': get_postgres_uri('warehouse_db'),
        'DATABASE_URL': get_postgres_uri('api_db'),
        'EXPLORER_URL': get_postgres_uri('explorer_db'),
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
