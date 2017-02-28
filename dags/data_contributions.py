import datetime
import airflow.operators
from airflow.models import DAG
import utils.helpers as helpers

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2017, 3, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=10),
}

dag = DAG(
    dag_id='data_contributions',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@daily'
)

unprocessed_data_contributions_sensor_task = airflow.operators.SqlSensor(
    task_id='unprocessed_data_contributions_sensor',
    dag=dag,
    conn_id='explorer_db',
    sql='SELECT id FROM data_contributions WHERE approved=true AND document_id IS NULL'
)

data_contributions_processor_task = helpers.create_processor_task(
    name='data_contributions',
    dag=dag
)

data_contributions_processor_task.set_upstream(unprocessed_data_contributions_sensor_task)
