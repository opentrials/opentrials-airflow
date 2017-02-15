try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest
from dags.operators.http_to_s3_transfer import HTTPToS3Transfer


class TestHTTPToS3Transfer(object):
    def test_its_created_successfully(self):
        operator = HTTPToS3Transfer(
            task_id='task_id',
            url='http://example.com/data.zip',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )
        assert operator

    @mock.patch('requests.get')
    @mock.patch('boto3.resource')
    @mock.patch('airflow.hooks.BaseHook.get_connection')
    def test_execute_streams_url_data_to_s3(self, get_connection_mock, boto3_mock, get_mock):
        get_connection_mock.return_value = mock.Mock(extra_dejson={
            'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
            'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
        })
        s3_bucket_mock = mock.Mock()
        s3_mock = mock.Mock()
        s3_mock.Bucket.return_value = s3_bucket_mock
        boto3_mock.return_value = s3_mock

        operator = HTTPToS3Transfer(
            task_id='task_id',
            url='http://example.com/data.zip',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )

        operator.execute(None)

        get_mock.assert_called_with(
            operator.url,
            params=operator.url_params,
            stream=True
        )

        s3_mock.Bucket.assert_called_with('bucket')
        s3_bucket_mock.upload_fileobj.assert_called_with(
            get_mock.return_value.raw,
            'key',
            Callback=mock.ANY
        )

    @mock.patch('airflow.hooks.BaseHook.get_connection')
    def test_execute_requires_aws_access_key_id_in_connection_extra(self, get_connection_mock):
        get_connection_mock.return_value = mock.Mock(extra_dejson={
            'aws_secret_access_key': 'AWS_SECRET_ACCESS_KEY',
        })

        operator = HTTPToS3Transfer(
            task_id='task_id',
            url='http://example.com/data.zip',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )

        with pytest.raises(KeyError) as excinfo:
            operator.execute(None)
        assert 'aws_access_key_id' in str(excinfo.value)

    @mock.patch('airflow.hooks.BaseHook.get_connection')
    def test_execute_requires_aws_secret_access_key_in_connection_extra(self, get_connection_mock):
        get_connection_mock.return_value = mock.Mock(extra_dejson={
            'aws_access_key_id': 'AWS_ACCESS_KEY_ID',
        })

        operator = HTTPToS3Transfer(
            task_id='task_id',
            url='http://example.com/data.zip',
            s3_conn_id='s3_conn_id',
            s3_url='s3://bucket/key'
        )

        with pytest.raises(KeyError) as excinfo:
            operator.execute(None)
        assert 'aws_secret_access_key' in str(excinfo.value)
