from datetime import datetime
import airflow.models
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2016, 12, 1),
    'retries': 1,
}

dag = airflow.models.DAG(
    dag_id='hra',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

collector_task = helpers.create_collector_task(
    name='hra',
    dag=dag,
    environment={
        'HRA_ENV': airflow.models.Variable.get('HRA_ENV'),
        'HRA_URL': airflow.models.Variable.get('HRA_URL'),
        'HRA_USER': airflow.models.Variable.get('HRA_USER'),
        'HRA_PASS': airflow.models.Variable.get('HRA_PASS'),
    }
)

processor_task = helpers.create_processor_task(
    name='hra',
    dag=dag
)

hra_linker_task = helpers.create_processor_task(
    name='hra_linker',
    dag=dag
)

processor_task.set_upstream(collector_task)
hra_linker_task.set_upstream(processor_task)
