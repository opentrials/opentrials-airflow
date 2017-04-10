import datetime
from airflow.models import DAG
from airflow.operators.latest_only_operator import LatestOnlyOperator
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 3, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=10),
}

dag = DAG(
    dag_id='data_contributions',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@daily'
)

latest_only_task = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag,
)

data_contributions_processor_task = helpers.create_processor_task(
    name='data_contributions',
    dag=dag
)

data_contributions_processor_task.set_upstream(latest_only_task)
