try:
    import unittest.mock as mock
except ImportError:
    import mock
import collections
import io
import shlex
import pytest
import airflow.exceptions
from dags.operators.docker_cli_operator import DockerCLIOperator


class TestDockerCLIOperator(object):
    def test_its_created_successfully(self):
        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command='true',
            environment={},
            force_pull=True
        )
        assert operator
        assert operator.task_id == 'task_id'

    def test_it_adds_DOCKER_API_VERSION_to_environment_if_received_api_version(self):
        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command='true',
            api_version='API_VERSION'
        )
        assert operator.environment['DOCKER_API_VERSION'] == operator.api_version

    def test_it_does_not_set_DOCKER_API_VERSION_to_environment_if_api_version_is_none(self):
        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command='true',
        )
        assert 'DOCKER_API_OPERATOR' not in operator.environment

    @mock.patch('subprocess.Popen', autospec=True)
    @mock.patch('logging.info', autospec=True)
    def test_run_command(self, logging_info_mock, popen_mock):
        command = 'command'
        command_output = [
            u'first line',
            u'second line',
        ]
        env = {
            'foo': 'bar',
        }
        process_mock = mock.Mock()
        process_mock.stdout = io.StringIO(u'\n'.join(command_output))
        process_mock.returncode = 0
        popen_mock.return_value = process_mock

        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command=command,
        )

        exit_code = operator._run_command(command, env)

        popen_mock.assert_called_with(
            shlex.split(command),
            env=env,
            stdout=mock.ANY,
            stderr=mock.ANY,
            preexec_fn=mock.ANY
        )
        logging_info_mock.assert_has_calls([
            mock.call(line) for line in command_output
        ])
        assert exit_code == process_mock.returncode

    @mock.patch('subprocess.Popen', autospec=True)
    def test_run_command_raises_airflowexception_if_command_failed(self, popen_mock):
        process_mock = mock.Mock()
        process_mock.stdout = io.StringIO(u'')
        process_mock.returncode = 1
        popen_mock.return_value = process_mock
        command = 'inexistent_command'

        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command=command,
        )

        with pytest.raises(airflow.exceptions.AirflowException):
            operator._run_command(command)

    def test_get_docker_run_command_works_without_environment(self):
        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command='command',
        )

        docker_command = operator._get_docker_run_command()

        assert docker_command == 'docker run --rm {image} {command}'.format(
            image=operator.image,
            command=operator.command
        )

    def test_get_docker_run_command_works_with_environment(self):
        environment = collections.OrderedDict([
            ('foo', 'bar baz'),
            ('bar', 'foo bar baz'),
        ])
        operator = DockerCLIOperator(
            task_id='task_id',
            image='docker/image:latest',
            command='command',
            environment=environment
        )

        docker_command = operator._get_docker_run_command()

        assert docker_command == 'docker run --rm --env "foo=$foo" --env "bar=$bar" {image} {command}'.format(
            image=operator.image,
            command=operator.command
        )

    @mock.patch('dags.operators.docker_cli_operator.DockerCLIOperator._run_command')
    def test_pull_image_runs_the_correct_command(self, run_command_mock):
        operator = DockerCLIOperator(
            task_id='task_id',
            image='alpine:latest',
            command='true'
        )

        exit_code = operator._pull_image()

        run_command_mock.assert_called_with(
            'docker pull {}'.format(operator.image),
            operator.environment
        )
        assert exit_code == run_command_mock()
