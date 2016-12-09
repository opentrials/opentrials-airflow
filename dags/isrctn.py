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

dag = DAG(dag_id='isrctn',
          default_args=args,
          max_active_runs=1,
          schedule_interval='@monthly')

collector_task = DockerOperator(
    task_id='irctn_collector',
    dag=dag,
    image='okibot/collectors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'PYTHON_ENV': Variable.get('ENV'),
        'DOWNLOAD_DELAY': Variable.get('DOWNLOAD_DELAY'),
    },
    command='make start irctn'
)

processor_task = DockerOperator(
    task_id='irctn_processor',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
    },
    command='make start irctn'
)

merge_trials_identifiers_task = DockerOperator(
    task_id='merge_trials_identifiers',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
    },
    command='make start merge_trials_identifiers'

)

processor_task.set_upstream(collector_task)
merge_trials_identifiers_task.set_upstream(processor_task)
