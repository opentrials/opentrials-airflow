import datetime
import airflow.models
import utils.helpers as helpers
from operators.python_sensor import PythonSensor

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2016, 12, 1),
    'retries': 1,
}

dag = airflow.models.DAG(
    dag_id='hra',
    default_args=args,
    max_active_runs=1,
    schedule_interval='@monthly'
)


def _check_hra_api_availability():
    now = datetime.datetime.now()

    is_mon_wed_or_thursday = (now.weekday() in [0, 2, 3])
    is_after_6am = (now.time() >= datetime.time(6, 0))
    is_before_8am = (now.time() < datetime.time(8, 0))
    is_between_6am_and_8am = (is_after_6am and is_before_8am)

    return is_mon_wed_or_thursday and is_between_6am_and_8am


wait_for_hra_api_availability_sensor = PythonSensor(
    task_id='wait_for_hra_api_availability',
    dag=dag,
    python_callable=_check_hra_api_availability
)

collector_task = helpers.create_collector_task(
    name='hra',
    dag=dag,
    environment={
        'HRA_ENV': airflow.models.Variable.get('HRA_ENV'),
        'HRA_URL': airflow.models.Variable.get('HRA_URL'),
        'HRA_USER': airflow.models.Variable.get('HRA_USER'),
        'HRA_PASS': airflow.models.Variable.get('HRA_PASS'),
    }
)

processor_task = helpers.create_processor_task(
    name='hra',
    dag=dag
)

collector_task.set_upstream(wait_for_hra_api_availability_sensor)
processor_task.set_upstream(collector_task)
