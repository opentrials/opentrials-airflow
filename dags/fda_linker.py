import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG, Variable
import utils.helpers as helpers


args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(dag_id='fda_linker',
          default_args=args,
          max_active_runs=1,
          schedule_interval='@monthly')

sync_text_task = DockerOperator(
    task_id='sync_text_from_documentcloud',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
    },
    command='make start sync_text_from_documentcloud'
)

linker_task = DockerOperator(
    task_id='fda_linker',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
    },
    command='make start fda_linker'
)

linker_task.set_upstream(sync_text_task)
