import datetime
from airflow.models import DAG
from airflow.operators.latest_only_operator import LatestOnlyOperator
import utils.helpers as helpers
from operators.heroku_operator import HerokuOperator


args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 1, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(hours=1),
}

dag = DAG(
    dag_id='merge_identifiers_and_reindex',
    default_args=args,
    max_active_runs=1,
    schedule_interval=None
)

latest_only = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag,
)

merge_trials_identifiers_task = helpers.create_processor_task(
    name='merge_trials_identifiers',
    dag=dag
)

reindex_elasticsearch_task = HerokuOperator(
    task_id='reindex_elasticsearch',
    dag=dag,
    app_name='ot-api',
    heroku_conn_id='heroku_conn',
    command='npm run reindex'
)

merge_trials_identifiers_task.set_upstream(latest_only)
reindex_elasticsearch_task.set_upstream(merge_trials_identifiers_task)
