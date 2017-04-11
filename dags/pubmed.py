import datetime
from airflow.models import DAG
from airflow.operators.latest_only_operator import LatestOnlyOperator
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 4, 1),
    'retries': 1,
}

dag = DAG(
    dag_id='pubmed',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

latest_only_task = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag,
)

collector_task = helpers.create_collector_task(
    name='pubmed',
    dag=dag,
    command='make start pubmed 1900-01-01 2100-01-01'
)

unregistered_trials_task = helpers.create_processor_task(
    name='pubmed_unregistered_trials',
    dag=dag
)

trials_remover_task = helpers.create_processor_task(
    name='trial_remover',
    dag=dag
)

pubmed_publications_task = helpers.create_processor_task(
    name='pubmed_publications',
    dag=dag
)

merge_identifiers_and_reindex_task = helpers.create_trigger_subdag_task(
    trigger_dag_id='merge_identifiers_and_reindex',
    dag=dag
)

collector_task.set_upstream(latest_only_task)
unregistered_trials_task.set_upstream(collector_task)
trials_remover_task.set_upstream(unregistered_trials_task)
pubmed_publications_task.set_upstream(trials_remover_task)
merge_identifiers_and_reindex_task.set_upstream(pubmed_publications_task)
