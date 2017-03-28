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
    dag_id='pubmed',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

collector_task = helpers.create_collector_task(
    name='pubmed',
    dag=dag,
    command='make start pubmed 1900-01-01 2100-01-01'
)

unregistred_trials_task = helpers.create_processor_task(
    name='pubmed_unregistered_trials',
    dag=dag
)

trials_remover_task = helpers.create_processor_task(
    name='trial_remover',
    dag=dag
)

publications_task = helpers.create_processor_task(
    name='pubmed_publications',
    dag=dag
)


unregistred_trials_task.set_upstream(collector_task)
trials_remover_task.set_upstream(unregistred_trials_task)
publications_task.set_upstream(trials_remover_task)
