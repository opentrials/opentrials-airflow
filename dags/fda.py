import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.models import DAG, Variable
from dags.subdag import sub_dag
import utils.helpers as helpers


args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(dag_id='fda',
          default_args=args,
          max_active_runs=1,
          schedule_interval='@monthly')

fda_dap = SubDagOperator(
    subdag=sub_dag('fda', 'fda_dap', dag.start_date, dag.schedule_interval),
    task_id=CHILD_DAG_NAME,
    dag=dag,
)

fda_linker = SubDagOperator(
    subdag=sub_dag('fda', 'fda_dap', dag.start_date, dag.schedule_interval),
    task_id=CHILD_DAG_NAME,
    dag=dag,
)

remove_unknown_documentcloud_docs_task = DockerOperator(
    task_id='remove_unknown_documentcloud_docs',
    dag=dag,
    image='okibot/processors:latest',
    force_pull=True,
    environment={
        'WAREHOUSE_URL': helpers.get_postgres_uri('warehouse_db'),
        'DATABASE_URL': helpers.get_postgres_uri('api_db'),
        'EXPLORERDB_URL': helpers.get_postgres_uri('explorer_db'),
        'LOGGING_URL': Variable.get('LOGGING_URL'),
        'DOCUMENTCLOUD_USERNAME': Variable.get('DOCUMENTCLOUD_USERNAME'),
        'DOCUMENTCLOUD_PASSWORD': Variable.get('DOCUMENTCLOUD_PASSWORD'),
        'DOCUMENTCLOUD_PROJECT': Variable.get('DOCUMENTCLOUD_PROJECT'),
    },
    command='make start remove_unknown_documentcloud_docs'
)

remove_unknown_documentcloud_docs_task.set_upstream(fda_linker)
fda_linker.set_upstream(fda_dap)
