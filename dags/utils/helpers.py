import airflow.hooks


def get_postgres_uri(name):
    conn = airflow.hooks.BaseHook.get_connection(name)
    if not conn:
        return

    uri = 'postgres://{user}:{password}@{host}:{port}/{schema}'
    return uri.format(
        user=conn.login,
        password=conn.password,
        host=conn.host,
        port=conn.port or 5432,
        schema=conn.schema
    )
