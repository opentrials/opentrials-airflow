import os
import pytest
import airflow.models


class TestDAGS(object):
    def test_it_can_be_imported(self, dagbag):
        # The error messages in Airflow 1.8 look like "u'Error message'", so we
        # clean them before checking what they are.
        clear_exc_message = lambda err: err.strip("u'")  # noqa: E731

        is_sql_error = lambda err: err.startswith('(sqlite3.OperationalError)')  # noqa: E731
        is_conn_error = lambda err: err.startswith('The conn_id')  # noqa: E731
        is_variable_error = lambda err: err.startswith('Variable ')  # noqa: E731
        import_errors = [
            error for error in dagbag.import_errors.values()
            if (not is_sql_error(clear_exc_message(error)) and
                not is_conn_error(clear_exc_message(error)) and
                not is_variable_error(clear_exc_message(error)))
        ]

        assert not import_errors


@pytest.fixture
def dagbag():
    dag_folder = os.getenv('AIRFLOW_DAGS')
    assert dag_folder, 'AIRFLOW_DAGS must be defined'
    return airflow.models.DagBag(dag_folder=dag_folder, include_examples=False)
