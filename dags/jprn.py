import datetime
from airflow.models import DAG
from airflow.operators.latest_only_operator import LatestOnlyOperator
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.utcnow(),
    'retries': 1,
}

dag = DAG(
    dag_id='jprn',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

latest_only_task = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag,
)

collector_task = helpers.create_collector_task(
    name='jprn',
    dag=dag,
    command='make start jprn 1 100000'
)

processor_task = helpers.create_processor_task(
    name='jprn',
    dag=dag
)

merge_identifiers_and_reindex_task = helpers.create_trigger_subdag_task(
    trigger_dag_id='merge_identifiers_and_reindex',
    dag=dag
)

collector_task.set_upstream(latest_only_task)
processor_task.set_upstream(collector_task)
merge_identifiers_and_reindex_task.set_upstream(processor_task)
