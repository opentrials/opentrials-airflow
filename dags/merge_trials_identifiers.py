import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG
import airflow.hooks


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


args = {
    'owner': 'vitorbaptista',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(dag_id='run_docker',
          default_args=args,
          schedule_interval=datetime.timedelta(1))

DockerOperator(
    task_id='merge_trials_identifiers',
    dag=dag,
    image='okibot/processors:latest',
    environment={
        'WAREHOUSE_URL': get_postgres_uri('warehouse_db'),
        'DATABASE_URL': get_postgres_uri('api_db'),
        'EXPLORERDB_URL': get_postgres_uri('explorer_db'),
        'LOGGING_URL': '',
    },
    command='make start merge_trials_identifiers'
)
