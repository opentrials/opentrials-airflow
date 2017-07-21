import airflow.models
import airflow.exceptions
import airflow.hooks.base_hook
from airflow.utils.decorators import apply_defaults

import copy
import logging
import os
import shlex
import signal
import subprocess


class DockerCLIOperator(airflow.models.BaseOperator):
    '''Executes a command on a Docker comtainer.

    This uses bash to execute Docker commands instead of using the Docker API
    to try to work around issue
    https://issues.apache.org/jira/browse/AIRFLOW-1131

    :param image: Docker image from which to create the container.
    :type image: str
    :param command: Command to run (templated)
    :type command: str
    :param environment: Environment variables to set in the container.
    :type environment: dict
    :param force_pull: Pull the docker image on every run (default: False).
    :type force_pull: bool
    '''
    template_fields = ('command',)

    @apply_defaults
    def __init__(
            self,
            image,
            command,
            environment=None,
            force_pull=False,
            api_version=None,
            *args,
            **kwargs
    ):
        super(DockerCLIOperator, self).__init__(*args, **kwargs)
        self.image = image
        self.command = command
        self.environment = copy.deepcopy(environment or {})
        self.force_pull = force_pull
        self.api_version = api_version
        self._process = None

        if self.api_version:
            self.environment['DOCKER_API_VERSION'] = self.api_version

    def execute(self, context):
        if self.force_pull:
            self._pull_image()

        docker_run_command = self._get_docker_run_command()
        return self._run_command(docker_run_command, self.environment)

    def on_kill(self):
        if self._process:
            logging.info('Sending SIGTERM signal to process group')
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)

    def _pull_image(self):
        pull_command = 'docker pull {image}'.format(image=self.image)
        return self._run_command(pull_command, self.environment)

    def _get_docker_run_command(self):
        env_params = [
            '--env "{key}=${key}"'.format(key=key)
            for key, value in self.environment.items()
            if value is not None
        ]
        resource_limits_params = [
            '--memory=350m',
            '--cpu-period=100000',
            '--cpu-quota=50000',
        ]

        docker_command = [
            'docker',
            'run',
            '--rm',
        ] + resource_limits_params + [
        ] + env_params + [
            self.image,
            self.command,
        ]

        return ' '.join(docker_command)

    def _run_command(self, command, env=None):
        command = '/bin/bash -c "{command}"'.format(command=command)
        logging.info('Running command "{}"'.format(shlex.split(command)))
        self._process = subprocess.Popen(
            shlex.split(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=_remove_nulls_and_encode_as_utf8_strings(env),
            preexec_fn=os.setsid
        )
        process = self._process

        line = ''
        for line in iter(process.stdout.readline, b''):
            line = line.decode('utf-8').strip()
            logging.info(line)
        process.wait()
        logging.info('Command exited with '
                     'return code {0}'.format(process.returncode))

        if process.returncode != 0:
            msg = 'Bash command "{command}" failed with exit code "{exitcode}"'.format(
                command=command,
                exitcode=process.returncode
            )
            raise airflow.exceptions.AirflowException(msg)

        return process.returncode


def _remove_nulls_and_encode_as_utf8_strings(env):
    '''This prepares the dict to be used as environments in subprocess

    The environment dict passed to subprocess.Popen() can't contain non-string
    values, and they need to be encoded as byte strings.
    '''
    if not hasattr(env, 'items'):
        return env

    result = {}

    for key, value in env.items():
        if value is None:
            continue

        encoded_key = key.encode('utf-8')
        encoded_value = str(value)

        if hasattr(encoded_value, 'encode'):
            encoded_value = encoded_value.encode('utf-8')

        result[encoded_key] = encoded_value

    return result
