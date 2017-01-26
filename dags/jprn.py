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
    dag_id='jprn',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
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

merge_trials_identifiers_task = helpers.create_processor_task(
    name='merge_trials_identifiers',
    dag=dag
)

processor_task.set_upstream(collector_task)
merge_trials_identifiers_task.set_upstream(processor_task)
