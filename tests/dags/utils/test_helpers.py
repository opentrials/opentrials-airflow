try:
    import unittest.mock as mock
except ImportError:
    import mock
import datetime
import airflow.models
import dags.utils.helpers as helpers


class TestGetPostgresUriHelper(object):
    @mock.patch('airflow.hooks.base_hook.BaseHook')
    def test_generates_the_correct_postgres_uri(self, basehook_mock):
        connection_mock = mock.Mock(
            login='login',
            password='password',
            host='host',
            port=1234,
            schema='schema'
        )
        basehook_mock.get_connection.return_value = connection_mock

        uri = helpers.get_postgres_uri('connection')
        assert uri == 'postgres://login:password@host:1234/schema'

    @mock.patch('airflow.hooks.base_hook.BaseHook')
    def test_uses_port_5432_by_default(self, basehook_mock):
        connection_mock = mock.Mock(
            port=None
        )
        basehook_mock.get_connection.return_value = connection_mock

        uri = helpers.get_postgres_uri('connection')
        assert ':5432' in uri


class TestCreateTasks(object):
    DEFAULT_ENV_KEYS = [
        'WAREHOUSE_URL',
        'DATABASE_URL',
        'EXPLORER_URL',
        'PYTHON_ENV',
        'LOGGING_URL',
        'DOWNLOAD_DELAY',
        'SENTRY_DSN',
        'DOCKER_API_VERSION',
    ]

    def test_create_collector_task_returns_tasks_with_correct_options(self):
        dag = None
        with mock.patch('airflow.hooks.base_hook.BaseHook'), mock.patch('airflow.models.Variable'):
            task = helpers.create_collector_task('foo', dag)

        assert task.task_id == 'collector_foo'
        assert task.image == 'opentrials/collectors:latest'
        assert task.force_pull
        assert sorted(task.environment.keys()) == sorted(self.DEFAULT_ENV_KEYS)

    def test_create_collector_task_allows_changing_command(self):
        dag = None
        command = 'sleep'
        with mock.patch('airflow.hooks.base_hook.BaseHook'), mock.patch('airflow.models.Variable'):
            task = helpers.create_collector_task('foo', dag, command)

        assert task.command == command

    def test_create_processor_task_returns_tasks_with_correct_options(self):
        dag = None
        with mock.patch('airflow.hooks.base_hook.BaseHook'), mock.patch('airflow.models.Variable'):
            task = helpers.create_processor_task('foo', dag)

        assert task.task_id == 'processor_foo'
        assert task.image == 'opentrials/processors:latest'
        assert task.force_pull
        assert sorted(task.environment.keys()) == sorted(self.DEFAULT_ENV_KEYS)


class TestCreateTriggerSubdagTask(object):
    def test_creates_task_with_correct_params(self):
        dag = airflow.models.DAG(
            dag_id='my_dag',
            start_date=datetime.datetime(2017, 1, 1)
        )
        trigger_dag_id = 'target_dag'
        trigger_task = helpers.create_trigger_subdag_task(trigger_dag_id, dag)

        expected_task_id = 'trigger_{}_from_{}'.format(trigger_dag_id, dag.dag_id)
        assert trigger_task is not None
        assert trigger_task.task_id == expected_task_id
        assert trigger_task.dag == dag
        assert trigger_task.trigger_dag_id == trigger_dag_id
