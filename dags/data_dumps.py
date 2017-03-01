import datetime
import airflow
from airflow.models import DAG
from operators.postgres_to_s3_transfer import PostgresToS3Transfer

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 3, 15),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=10),
}

dag = DAG(
    dag_id='data_dumps',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)

tables_to_dump = [
    'conditions',
    'document_categories',
    'documents',
    'fda_applications',
    'fda_approvals',
    'files',
    'interventions',
    'knex_migrations',
    'knex_migrations_id_seq',
    'knex_migrations_lock',
    'locations',
    'organisations',
    'persons',
    'publications',
    'records',
    'risk_of_bias_criterias',
    'risk_of_biases',
    'risk_of_biases_risk_of_bias_criterias',
    'sources',
    'trials',
    'trials_conditions',
    'trials_documents',
    'trials_interventions',
    'trials_locations',
    'trials_organisations',
    'trials_persons',
    'trials_publications',
]
datastore_http = airflow.hooks.BaseHook.get_connection('datastore_http')
DUMP_API_URL = '{base}{endpoint}'.format(
    base=datastore_http.host.replace('http://', 's3://'),
    endpoint='/dumps/opentrials-api-{{ end_date }}.dump'
)
dump_api_database = PostgresToS3Transfer(
    task_id='dump_api_database',
    dag=dag,
    postgres_conn_id='api_db',
    tables=tables_to_dump,
    s3_conn_id='datastore_s3',
    s3_url=DUMP_API_URL
)
