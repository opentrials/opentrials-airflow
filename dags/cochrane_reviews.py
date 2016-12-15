from datetime import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG, Variable
import utils.helpers as helpers
import os

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.strptime('Dec 1 2016', '%b %d %Y'),
    'retries': 1,
}

dag = DAG(dag_id='cochrane_reviews',
          default_args=args,
          max_active_runs=1,
          schedule_interval='@monthly')

collector_task = DockerOperator(
    task_id='cochrane_reviews_collector',
    dag=dag,
    image='okibot/collectors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'COCHRANE_ARCHIVE_URL': Variable.get('COCHRANE_ARCHIVE_URL'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'PYTHON_ENV': Variable.get('ENV'),
        'FERNET_KEY': os.environ['FERNET_KEY'],
    },
    command='make start cochrane_reviews'
)

processor_task = DockerOperator(
    task_id='cochrane_reviews_processor',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'FERNET_KEY': os.environ['FERNET_KEY'],
    },
    command='make start cochrane_reviews'
)

processor_task.set_upstream(collector_task)
