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

processor_task = helpers.create_processor_task(
    name='pubmed',
    dag=dag
)

pubmed_linker_task = helpers.create_processor_task(
    name='pubmed_linker',
    dag=dag
)

processor_task.set_upstream(collector_task)
pubmed_linker_task.set_upstream(processor_task)
