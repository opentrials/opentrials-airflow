try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
import airflow.exceptions
import requests.exceptions
from dags.operators.heroku_operator import HerokuOperator


class TestHerokuOperator(object):
    def test_its_created_successfully(self):
        operator = HerokuOperator(
            task_id='task_id',
            command='true',
            app_name='app_name',
            heroku_conn_id='heroku_conn_id'
        )
        assert operator
        assert operator.task_id == 'task_id'

    @mock.patch('heroku3.from_key')
    @mock.patch('airflow.hooks.BaseHook.get_connection')
    def test_it_uses_the_connection_password_as_api_key(self, get_connection_mock, heroku3_from_key_mock):
        operator = HerokuOperator(
            task_id='task_id',
            command='true',
            app_name='app_name',
            heroku_conn_id='heroku_conn_id'
        )

        try:
            operator.execute(None)
        except Exception:
            pass

        heroku3_from_key_mock.assert_called_with(get_connection_mock().password)

    @mock.patch('heroku3.from_key')
    @mock.patch('logging.info')
    @mock.patch('airflow.hooks.BaseHook.get_connection')
    def test_logs_the_commands_output(self, _, logging_info_mock, heroku3_from_key_mock):
        conn_mock = mock.MagicMock()
        conn_mock.stream_app_log.return_value = [
            'first line',
            'second line',
            'heroku[run.8185]: Process exited with status 0',
        ]
        heroku3_from_key_mock.return_value = conn_mock

        operator = HerokuOperator(
            task_id='task_id',
            command='true',
            app_name='app_name',
            heroku_conn_id='heroku_conn_id'
        )

        operator.execute(None)

        logging_info_mock.assert_has_calls([
            mock.call(line) for line in conn_mock.stream_app_log()
        ])

    @mock.patch('heroku3.from_key')
    @mock.patch('logging.info')
    @mock.patch('airflow.hooks.BaseHook.get_connection')
    def test_raises_if_command_is_unsuccessful(self, _, logging_info_mock, heroku3_from_key_mock):
        conn_mock = mock.MagicMock()
        conn_mock.stream_app_log.side_effect = requests.exceptions.ConnectionError()
        dyno = conn_mock.run_command_on_app()
        conn_mock.get_app_log.return_value = 'heroku[{}]: Process exited with status -1'.format(dyno.name)
        heroku3_from_key_mock.return_value = conn_mock

        operator = HerokuOperator(
            task_id='task_id',
            command='false',
            app_name='app_name',
            heroku_conn_id='heroku_conn_id'
        )

        with pytest.raises(airflow.exceptions.AirflowException):
            operator.execute(None)
