import pytest
from dags.operators.python_sensor import PythonSensor


class TestPythonSensor(object):
    @pytest.mark.parametrize('return_value, result', [
        ('a string', False),
        (42, False),
        (0, False),
        (False, False),
        (True, True),
    ])
    def test_poke_returns_false_if_callable_doesnt_return_true(self, return_value, result):
        callable = lambda: return_value  # noqa: E731

        sensor = PythonSensor(
            task_id='task_id',
            python_callable=callable
        )

        assert sensor.poke(None) is result
