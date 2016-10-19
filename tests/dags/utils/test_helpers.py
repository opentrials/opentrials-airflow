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
