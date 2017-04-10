import datetime
import airflow.hooks.base_hook
from airflow.models import DAG
from airflow.operators.latest_only_operator import LatestOnlyOperator
import utils.helpers as helpers
from operators.http_to_s3_transfer import HTTPToS3Transfer

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 1, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=10),
}

dag = DAG(
    dag_id='nct',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

HTTP_CONN_ID = 'datastore_http'
S3_BASE_URL = airflow.hooks.base_hook.BaseHook.get_connection(HTTP_CONN_ID).host
S3_URL_ENDPOINT = '/dumps/sources/nct_2001-01-01_{{ end_date }}.zip'
NCT_DATA_URL = '{base}{endpoint}'.format(
    base=S3_BASE_URL,
    endpoint=S3_URL_ENDPOINT
)

latest_only_task = LatestOnlyOperator(
    task_id='latest_only',
    dag=dag,
)

save_nct_xml_to_s3_task = HTTPToS3Transfer(
    task_id='save_nct_xml_to_s3',
    dag=dag,
    url='https://clinicaltrials.gov/search',
    url_params={
        'resultsxml': 'True',
        'rcv_s': '01/01/2001',
        'rcv_e': '{{ macros.ds_format(end_date, "%Y-%m-%d", "%d/%m/%Y") }}',
    },
    s3_conn_id='datastore_s3',
    s3_url=NCT_DATA_URL.replace('http://', 's3://'),
)

collector_task = helpers.create_collector_task(
    name='nct',
    dag=dag,
    command='make start nct {url}'.format(url=NCT_DATA_URL)
)

processor_task = helpers.create_processor_task(
    name='nct',
    dag=dag
)

merge_identifiers_and_reindex_task = helpers.create_trigger_subdag_task(
    trigger_dag_id='merge_identifiers_and_reindex',
    dag=dag
)

save_nct_xml_to_s3_task.set_upstream(latest_only_task)
collector_task.set_upstream(save_nct_xml_to_s3_task)
processor_task.set_upstream(collector_task)
merge_identifiers_and_reindex_task.set_upstream(processor_task)
