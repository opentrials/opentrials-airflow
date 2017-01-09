from datetime import datetime
from airflow.models import DAG
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2016, 12, 1),
    'retries': 1,
}

dag = DAG(
    dag_id='cochrane_reviews',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

collector_task = helpers.create_collector_task(
    name='cochrane_reviews',
    dag=dag
)

processor_task = helpers.create_processor_task(
    name='cochrane_reviews',
    dag=dag
)

processor_task.set_upstream(collector_task)
