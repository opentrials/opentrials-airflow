import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG, Variable
from .utils import helpers


args = {
    'owner': 'vitorbaptista',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(dag_id='fda_dap',
          default_args=args,
          max_active_runs=1,
          schedule_interval='@monthly')

collector_task = DockerOperator(
    task_id='fda_dap_collector',
    dag=dag,
    image='okibot/collectors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'PYTHON_ENV': Variable.get('ENV'),
    },
    command='make start fda_dap'
)

processor_task = DockerOperator(
    task_id='fda_dap_processor',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'AWS_ACCESS_KEY_ID': Variable.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': Variable.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_S3_BUCKET': Variable.get('AWS_S3_BUCKET'),
        'AWS_S3_REGION': Variable.get('AWS_S3_REGION'),
        'AWS_S3_CUSTOM_DOMAIN': Variable.get('AWS_S3_CUSTOM_DOMAIN'),
        'DOCUMENTCLOUD_USERNAME': Variable.get('DOCUMENTCLOUD_USERNAME'),
        'DOCUMENTCLOUD_PASSWORD': Variable.get('DOCUMENTCLOUD_PASSWORD'),
        'DOCUMENTCLOUD_PROJECT': Variable.get('DOCUMENTCLOUD_PROJECT'),
    },
    command='make start fda_dap'
)

processor_task.set_upstream(collector_task)
