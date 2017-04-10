import airflow.models
import airflow.exceptions
import airflow.hooks.base_hook
from airflow.utils.decorators import apply_defaults

import re
import logging
import heroku3
import requests.exceptions


class HerokuOperator(airflow.models.BaseOperator):
    '''Executes a command on a Heroku dyno.

    :param heroku_conn_id: Heroku's connection ID. It should contain your API
        key in the password field.
    :type heroku_conn_id: str
    :param app_name: Heroku's app name.
    :type app_name: str
    :param command: Command to run (templated)
    :type command: str
    :param size: Dyno's size (default: 'free')
    :type size: str
    :param timeout: Timeout on all HTTP requests (default: 60)
    :type timeout: int
    '''
    template_fields = ('command',)

    @apply_defaults
    def __init__(
            self,
            heroku_conn_id,
            app_name,
            command,
            size='free',
            timeout=60,
            *args,
            **kwargs
    ):
        super(HerokuOperator, self).__init__(*args, **kwargs)
        self.heroku_conn_id = heroku_conn_id
        self.app_name = app_name
        self.command = command
        self.size = size
        self.timeout = timeout
        self.dyno = None

    def execute(self, context):
        conn = airflow.hooks.base_hook.BaseHook.get_connection(self.heroku_conn_id)
        api_key = conn.password
        self.heroku_conn = heroku3.from_key(api_key)

        self.dyno = self.heroku_conn.run_command_on_app(
            self.app_name,
            self.command,
            size=self.size,
            attach=False,
            printout=False
        )

        try:
            status_code = None
            for line in self.heroku_conn.stream_app_log(
                    self.app_name,
                    dyno=self.dyno.name,
                    lines=1,
                    timeout=self.timeout
            ):
                logging.info(line)
                status_code = self._parse_status_code(line)
                if status_code is not None:
                    break
        except requests.exceptions.ConnectionError:
            if self._get_dyno_status_code() is None:
                raise

        if status_code != 0:
            msg = 'Command "{command}" returned non-successful status code "{status}"'.format(
                command=self.command,
                status=status_code
            )
            raise airflow.exceptions.AirflowException(msg)

        return status_code

    def on_kill(self):
        if self.dyno:
            self.dyno.kill()

    def _get_dyno_status_code(self):
        logs = self.heroku_conn.get_app_log(
            self.app_name,
            dyno=self.dyno.name,
            timeout=self.timeout
        )
        return self._parse_status_code(logs)

    def _parse_status_code(self, line):
        status_code = None
        m = re.search(
            'heroku\[.+\]: Process exited with status (-?\d+)',
            line
        )

        if m:
            status_code = int(m.groups()[0])

        return status_code
