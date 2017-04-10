import datetime
from airflow.models import DAG
from airflow.operators.latest_only_operator import LatestOnlyOperator
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 1, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=10),
}

dag = DAG(
    dag_id='run_all_processors',
    default_args=args,
    max_active_runs=1,
    schedule_interval=None
)

latest_only = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag,
)

merge_identifiers_and_reindex = helpers.create_trigger_subdag_task(
    trigger_dag_id='merge_identifiers_and_reindex',
    dag=dag
)

PROCESSORS = [
    'nct',
    'euctr',
    'hra',
    'ictrp',
]
for processor in PROCESSORS:
    processor_task = helpers.create_processor_task(
        name=processor,
        dag=dag
    )
    processor_task.set_upstream(latest_only)
    processor_task.set_downstream(merge_identifiers_and_reindex)
