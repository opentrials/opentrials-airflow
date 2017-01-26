import unittest.mock as mock
import dags.utils.helpers as helpers


class TestGetPostgresUriHelper(object):
    @mock.patch('airflow.hooks.BaseHook')
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

    @mock.patch('airflow.hooks.BaseHook')
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
        'EXPLORERDB_URL',
        'PYTHON_ENV',
        'LOGGING_URL',
        'DOWNLOAD_DELAY',
    ]

    def test_create_collector_task_returns_tasks_with_correct_options(self):
        dag = None
        with mock.patch('airflow.hooks.BaseHook'), mock.patch('airflow.models.Variable'):
            task = helpers.create_collector_task('foo', dag)

        assert task.task_id == 'collector_foo'
        assert task.image == 'okibot/collectors:latest'
        assert task.force_pull
        assert sorted(task.environment.keys()) == sorted(self.DEFAULT_ENV_KEYS)

    def test_create_collector_task_allows_changing_command(self):
        dag = None
        command = 'sleep'
        with mock.patch('airflow.hooks.BaseHook'), mock.patch('airflow.models.Variable'):
            task = helpers.create_collector_task('foo', dag, command)

        assert task.command == command

    def test_create_processor_task_returns_tasks_with_correct_options(self):
        dag = None
        with mock.patch('airflow.hooks.BaseHook'), mock.patch('airflow.models.Variable'):
            task = helpers.create_processor_task('foo', dag)

        assert task.task_id == 'processor_foo'
        assert task.image == 'okibot/processors:latest'
        assert task.force_pull
        assert sorted(task.environment.keys()) == sorted(self.DEFAULT_ENV_KEYS)
