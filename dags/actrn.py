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
    dag_id='actrn',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

collector_task = helpers.create_collector_task(
    name='actrn',
    dag=dag,
    command='make start actrn 2001-01-01'
)

processor_task = helpers.create_processor_task(
    name='actrn',
    dag=dag
)

merge_identifiers_and_reindex_task = helpers.create_trigger_subdag_task(
    trigger_dag_id='merge_identifiers_and_reindex',
    dag=dag
)

processor_task.set_upstream(collector_task)
merge_identifiers_and_reindex_task.set_upstream(processor_task)
