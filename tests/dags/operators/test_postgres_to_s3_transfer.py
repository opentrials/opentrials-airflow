try:
    import unittest.mock as mock
except ImportError:
    import mock
import subprocess
import dags.utils.helpers as helpers
from dags.operators.postgres_to_s3_transfer import PostgresToS3Transfer


class TestPostgresToS3Transfer(object):
    def test_its_created_successfully(self):
        operator = PostgresToS3Transfer(
            task_id='task_id',
            postgres_conn_id='postgres_conn_id',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )
        assert operator
        assert operator.task_id == 'task_id'

    @mock.patch('subprocess.Popen')
    @mock.patch('boto3.resource', autospec=True)
    @mock.patch('airflow.hooks.base_hook.BaseHook.get_connection')
    def test_execute_streams_url_data_to_s3(self, get_connection_mock, boto3_mock, popen_mock):
        operator = PostgresToS3Transfer(
            task_id='task_id',
            postgres_conn_id='postgres_conn_id',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )

        operator.execute(None)

        boto3_mock().Bucket.assert_called_with('bucket')
        boto3_mock().Bucket().upload_fileobj.assert_called_with(
            popen_mock().stdout.__enter__(),  # Needs __enter__() because it's called in a context manager
            'key'
        )

    @mock.patch('subprocess.Popen')
    @mock.patch('boto3.resource', autospec=True)
    @mock.patch('airflow.hooks.base_hook.BaseHook.get_connection')
    def test_execute_calls_pg_dump_correctly(self, get_connection_mock, boto3_mock, popen_mock):
        operator = PostgresToS3Transfer(
            task_id='task_id',
            postgres_conn_id='postgres_conn_id',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )

        operator.execute(None)

        expected_command = [
            'pg_dump',
            '-Fc',
            helpers.get_postgres_uri(operator.postgres_conn_id),
        ]
        popen_mock.assert_called_with(expected_command, stdout=subprocess.PIPE)

    @mock.patch('subprocess.Popen')
    @mock.patch('boto3.resource', autospec=True)
    @mock.patch('airflow.hooks.base_hook.BaseHook.get_connection')
    def test_execute_dumps_only_whitelisted_tables(self, get_connection_mock, boto3_mock, popen_mock):
        tables = [
            'users',
            'log',
        ]
        operator = PostgresToS3Transfer(
            task_id='task_id',
            postgres_conn_id='postgres_conn_id',
            tables=tables,
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )

        operator.execute(None)

        popen_command = popen_mock.call_args[0][0]

        # Ignore executable and the Postgres URI, as the params need to be
        # between these two
        pg_dump_params_without_uri = popen_command[1:-1]
        for table in tables:
            assert '--table={}'.format(table) in pg_dump_params_without_uri
