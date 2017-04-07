from urllib.parse import urlparse
import subprocess
import logging
import boto3

import airflow.hooks.base_hook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import utils.helpers as helpers


class PostgresToS3Transfer(BaseOperator):
    '''Dumps a Postgres database to a S3 key

    :param url: URL to download. (templated)
    :type url: str
    :param postgres_conn_id: Postgres Connection's ID.
    :type postgres_conn_id: str
    :param tables: List of tables to export (optional, default exports all
        tables).
    :type tables: list of str
    :param s3_conn_id: S3 Connection's ID. It needs a JSON in the `extra` field
        with `aws_access_key_id` and `aws_secret_access_key`
    :type s3_conn_id: str
    :param s3_url: S3 url (e.g. `s3://my_bucket/my_key.zip`) (templated)
    :type s3_url: str
    '''
    template_fields = ('s3_url',)

    @apply_defaults
    def __init__(self, postgres_conn_id, s3_conn_id, s3_url, tables=None, *args, **kwargs):
        super(PostgresToS3Transfer, self).__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.tables = tables
        self.s3_conn_id = s3_conn_id
        self.s3_url = s3_url

    def execute(self, context):
        s3 = self._load_s3_connection(self.s3_conn_id)
        s3_bucket, s3_key = self._parse_s3_url(self.s3_url)
        command = [
            'pg_dump',
            '-Fc',
        ]

        if self.tables:
            tables_params = ['--table={}'.format(table) for table in self.tables]
            command.extend(tables_params)

        logging.info('Dumping database "%s" into "%s"', self.postgres_conn_id, self.s3_url)
        logging.info('Command: %s <POSTGRES_URI>', ' '.join(command))

        command.append(helpers.get_postgres_uri(self.postgres_conn_id))

        with subprocess.Popen(command, stdout=subprocess.PIPE).stdout as dump_file:
            s3.Bucket(s3_bucket) \
              .upload_fileobj(dump_file, s3_key)

    @staticmethod
    def _parse_s3_url(s3_url):
        parsed_url = urlparse(s3_url)
        if not parsed_url.netloc:
            raise airflow.exceptions.AirflowException('Please provide a bucket_name')
        else:
            bucket_name = parsed_url.netloc
            key = parsed_url.path.strip('/')
            return (bucket_name, key)

    def _load_s3_connection(self, conn_id):
        '''
        Parses the S3 connection and returns a Boto3 resource.

        This should be implementing using the S3Hook, but it currently uses
        boto (not boto3) which doesn't allow streaming.

        :return: Boto3 resource
        :rtype: boto3.resources.factory.s3.ServiceResource
        '''
        conn = airflow.hooks.base_hook.BaseHook.get_connection(conn_id)
        extra_dejson = conn.extra_dejson
        key_id = extra_dejson['aws_access_key_id']
        access_key = extra_dejson['aws_secret_access_key']

        s3 = boto3.resource(
            's3',
            aws_access_key_id=key_id,
            aws_secret_access_key=access_key
        )

        return s3
