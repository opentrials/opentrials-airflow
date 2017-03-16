try:
    import unittest.mock as mock
except ImportError:
    import mock
import datetime
import pytz
import pytest
import freezegun


class TestHRA(object):
    @pytest.mark.parametrize('current_datetime, result', [
        (datetime.datetime(2016, 5, 2, 3, tzinfo=pytz.UTC), False),
        (datetime.datetime(2016, 5, 2, 3, tzinfo=pytz.UTC), False),  # Monday 3am
        (datetime.datetime(2016, 5, 2, 9, tzinfo=pytz.UTC), False),  # Monday 9am
        (datetime.datetime(2016, 5, 2, 7, tzinfo=pytz.UTC), True),  # Monday
        (datetime.datetime(2016, 5, 4, 7, tzinfo=pytz.UTC), True),  # Wednsday
        (datetime.datetime(2016, 5, 5, 7, tzinfo=pytz.UTC), True),  # Thursday
        (datetime.datetime(2016, 5, 6, 7, tzinfo=pytz.UTC), False),
    ])
    def test_it_waits_for_hra_api_availability(self, current_datetime, result):
        with mock.patch('airflow.models.Variable'):
            with mock.patch('airflow.hooks.BaseHook'):
                import dags.hra
        with freezegun.freeze_time(current_datetime):
            assert dags.hra.wait_for_hra_api_availability_sensor.poke(None) is result
