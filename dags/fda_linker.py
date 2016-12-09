from datetime import datetime
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG, Variable
import utils.helpers as helpers

def fda_linker_subdag(parent_dag_name, child_dag_name, start_date, schedule_interval):

    args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime.utcnow(),
        'retries': 1,
    }

    dag = DAG(dag_id='%s.%s' % (parent_dag_name, child_dag_name),
              start_date=datetime.strptime('Dec 1 2016', '%b %d %Y'),
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

    return dag
