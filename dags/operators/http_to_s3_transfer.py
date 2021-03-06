from urllib.parse import urlparse
import logging
import contextlib
import requests
import boto3

import airflow.exceptions
import airflow.hooks.base_hook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class HTTPToS3Transfer(BaseOperator):
    '''
    Downloads an URL's contents and stream it to S3.


    :param url: URL to download. (templated)
    :type url: str
    :param s3_conn_id: S3 Connection's ID. It needs a JSON in the `extra` field
        with `aws_access_key_id` and `aws_secret_access_key`
    :type s3_conn_id: str
    :param s3_url: S3 url (e.g. `s3://my_bucket/my_key.zip`) (templated)
    :type s3_url: str
    '''
    template_fields = ('url', 'url_params', 's3_url')

    @apply_defaults
    def __init__(self, url, s3_conn_id, s3_url, url_params=None, *args, **kwargs):
        super(HTTPToS3Transfer, self).__init__(*args, **kwargs)
        self.url = url
        self.url_params = url_params
        self.s3_conn_id = s3_conn_id
        self.s3_url = s3_url

    def execute(self, context):
        s3 = self._load_s3_connection(self.s3_conn_id)
        s3_bucket, s3_key = self._parse_s3_url(self.s3_url)

        logging.info(
            'Streaming %s (params %s) to S3 (%s)',
            self.url,
            self.url_params,
            self.s3_url,
        )

        with contextlib.closing(requests.get(self.url, params=self.url_params, stream=True)) as response:
            s3.Bucket(s3_bucket) \
              .upload_fileobj(response.raw, s3_key, Callback=_progress_logger())

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


def _progress_logger():
    '''Closure to keep track and log the download progress.'''
    closure = {'total': 0}

    def log_progress(bytes_count):
        closure['total'] += bytes_count
        logging.info('Downloaded %d bytes', closure['total'])

    return log_progress
