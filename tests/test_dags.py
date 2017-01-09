import os
import pytest
import airflow.models


class TestDAGS(object):
    def test_it_can_be_imported(self, dagbag):
        is_sql_error = lambda err: err.startswith('(sqlite3.OperationalError)')  # noqa: E731
        is_conn_error = lambda err: err.startswith('The conn_id')  # noqa: E731
        import_errors = [error for error in dagbag.import_errors.values()
                         if not is_sql_error(error) and not is_conn_error(error)]

        assert not import_errors


@pytest.fixture
def dagbag():
    dag_folder = os.getenv('AIRFLOW_DAGS')
    assert dag_folder, 'AIRFLOW_DAGS must be defined'
    return airflow.models.DagBag(dag_folder=dag_folder, include_examples=False)
