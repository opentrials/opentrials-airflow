import airflow.operators.sensors
from airflow.utils.decorators import apply_defaults


class PythonSensor(airflow.operators.sensors.BaseSensorOperator):
    '''
    Runs Python callable until it returns `True`.

    :param python_callable: Python callable to run. It should return `True`
        when successful, any other values (even truthy ones) won't work.
    :type python_callable: function
    '''

    @apply_defaults
    def __init__(self, python_callable, *args, **kwargs):
        super(PythonSensor, self).__init__(*args, **kwargs)
        self.python_callable = python_callable

    def poke(self, context):
        return self.python_callable() is True
