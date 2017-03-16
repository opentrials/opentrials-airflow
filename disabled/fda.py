import os
from datetime import datetime
from airflow.models import DAG, Variable
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.subdag_operator import SubDagOperator
from fda_dap import fda_dap_subdag as fda_dap
import utils.helpers as helpers


args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2016, 12, 1),
    'retries': 1,
}

dag = DAG(
    dag_id='fda',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

fda_dap_task = SubDagOperator(
    dag=dag,
    subdag=fda_dap(parent_dag_name='fda',
                   child_dag_name='dap',
                   start_date=dag.start_date,
                   schedule_interval=dag.schedule_interval),
    task_id='dap',
)

fda_linker_task = SubDagOperator(
    dag=dag,
    subdag=fda_dap(parent_dag_name='fda',
                   child_dag_name='linker',
                   start_date=dag.start_date,
                   schedule_interval=dag.schedule_interval),
    task_id='linker',
)

remove_unknown_documentcloud_docs_task = DockerOperator(
    task_id='remove_unknown_documentcloud_docs',
    dag=dag,
    image='opentrials/processors:latest',
    force_pull=True,
    api_version='1.23',
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORER_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'DOCUMENTCLOUD_USERNAME': Variable.get('DOCUMENTCLOUD_USERNAME'),
        'DOCUMENTCLOUD_PASSWORD': Variable.get('DOCUMENTCLOUD_PASSWORD'),
        'DOCUMENTCLOUD_PROJECT': Variable.get('DOCUMENTCLOUD_PROJECT'),
        'FERNET_KEY': os.environ['FERNET_KEY'],
    },
    command='make start remove_unknown_documentcloud_docs'
)

remove_unknown_documentcloud_docs_task.set_upstream(fda_linker_task)
fda_linker_task.set_upstream(fda_dap_task)
