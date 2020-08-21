from tap_bigquery.sync_bigquery import _build_query as build_query


def test_column_construction():
    keys = {
        "table": "test.test.table",
        "columns": ["col0", "col1", "col2"],
        "datetime_key": "col0"
    }
    query = build_query(keys)
    expected = (
        "SELECT col0,col1,col2 FROM test.test.table WHERE 1=1 ORDER BY col0")
    assert query == expected


def test_datetime_key_insertion():
    keys = {
        "table": "test.test.table",
        "columns": ["col1", "col2"],
        "datetime_key": "col0"
    }
    query = build_query(keys)
    expected = (
        "SELECT col1,col2,col0 FROM test.test.table WHERE 1=1 ORDER BY col0")
    assert query == expected


def test_limit():
    keys = {
        "table": "test.test.table",
        "columns": ["col0", "col1", "col2"],
        "datetime_key": "col0"
    }
    query = build_query(keys, limit=10)
    expected = (
        "SELECT col0,col1,col2 FROM test.test.table WHERE 1=1" +
        " ORDER BY col0 LIMIT 10")
    assert query == expected


def test_filters():
    keys = {
        "table": "test.test.table",
        "columns": ["col0", "col1", "col2"],
        "datetime_key": "created_at"
    }
    filters = ["DATE_ADD(created_at, INTERVAL -7 DAY)",
               "state='CA'"]
    query = build_query(keys, filters=filters, limit=10)
    expected = (
        "SELECT col0,col1,col2,created_at FROM test.test.table" +
        " WHERE 1=1 AND DATE_ADD(created_at, INTERVAL -7 DAY)" +
        " AND state='CA' ORDER BY created_at LIMIT 10")
    assert query == expected
