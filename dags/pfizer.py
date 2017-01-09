import datetime
from airflow.models import DAG
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(
    dag_id='pfizer',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

collector_task = helpers.create_collector_task(
    name='pfizer_collector',
    dag=dag
)

processor_task = helpers.create_processor_task(
    name='pfizer_processor',
    dag=dag
)

processor_task.set_upstream(collector_task)
