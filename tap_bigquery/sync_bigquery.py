import datetime, json, time
import dateutil.parser

import singer
import singer.metrics as metrics

from google.cloud import bigquery

from . import utils
from . import json2schema


LOGGER = utils.get_logger(__name__)

# StitchData compatible timestamp meta data
#  https://www.stitchdata.com/docs/data-structure/system-tables-and-columns
# The timestamp of the record extracted from the source
EXTRACT_TIMESTAMP = "_sdc_extracted_at"
# The timestamp of the record submit to the destination
# (kept null at extraction)
BATCH_TIMESTAMP = "_sdc_batched_at"
# Legacy timestamp field
LEGACY_TIMESTAMP = "_etl_tstamp"

BOOKMARK_KEY_NAME = "last_update"


def do_discover(stream, limit=100, output_schema_file=None,
                add_timestamp=True):
    client = bigquery.Client()
    filters = ""
    if stream.get("filters", None):
        filters = "AND " + "AND ".join(stream["filters"])
    keys = {"table": stream["table"],
            "columns": ",".join(stream["columns"]),
            "filters": filters,
            "limit": limit}
    query = ("SELECT {columns} FROM {table} WHERE 1=1 " +
             "{filters} LIMIT {limit}").format(**keys)

    LOGGER.info("Running query:\n    " + query)

    query_job = client.query(query)
    results = query_job.result()  # Waits for job to complete.

    data = []
    # Read everything upfront
    for row in results:
        record = {}
        for key in row.keys():
            record[key] = row[key]
        data.append(record)

    schema = json2schema.infer_schema(data)
    if add_timestamp:
        timestamp_format = {"type": ["null", "string"],
                            "format": "date-time"}
        schema["properties"][EXTRACT_TIMESTAMP] = timestamp_format
        schema["properties"][BATCH_TIMESTAMP] = timestamp_format
        # Support the legacy field
        schema["properties"][LEGACY_TIMESTAMP] = {"type": ["null", "number"],
                                                  "inclusion": "automatic"}

    if output_schema_file:
        with open(output_schema_file, "w") as f:
            json.dump(schema, f, indent=2)

    stream_metadata = [{
        "metadata": {
            "selected": True,
            "table": stream["table"],
            "columns": stream["columns"],
            "filters": stream.get("filters", []),
            "datetime_key": stream["datetime_key"]
            # "inclusion": "available",
            # "table-key-properties": ["id"],
            # "valid-replication-keys": ["date_modified"],
            # "schema-name": "users"
            },
        "breadcrumb": []
        }]

    # TODO: Need to put something in here?
    key_properties = []

    catalog = {"selected": True,
               "type": "SCHEMA",
               "stream": stream["name"],
               "key_properties": key_properties,
               "properties": schema["properties"]
               }

    return stream_metadata, key_properties, catalog


def get_start(config, state, tap_stream_id, key):
    current_bookmark = singer.get_bookmark(state, tap_stream_id, key)
    if not current_bookmark and config.get("start_datetime"):
        current_bookmark = dateutil.parser.parse(config.get("start_datetime")).strftime("%Y-%m-%d %H:%M:%S")
    return current_bookmark


def _build_query(keys, filters):
    query = "SELECT {columns} FROM {table} WHERE 1=1".format(**keys)

    if filters:
        for f in filters:
            query = query + " AND " + f

    if keys.get("datetime_key") and keys.get("start_datetime"):
        query = (query +
                 " AND datetime '{start_datetime}' <= CAST({datetime_key} as datetime)".format(
                     **keys))
    if keys.get("datetime_key") and keys.get("end_datetime"):
        query = (query +
                 " AND CAST({datetime_key} as datetime) < datetime '{end_datetime}'".format(
                     **keys))
    if keys.get("datetime_key"):
        query = (query + " ORDER BY {datetime_key}".format(**keys))

    return query


def do_sync(config, state, stream):
    client = bigquery.Client()
    metadata = stream.metadata[0]["metadata"]
    tap_stream_id = stream.tap_stream_id

    start_datetime = get_start(config, state, tap_stream_id, BOOKMARK_KEY_NAME)
    if config.get("end_datetime"):
        end_datetime = dateutil.parser.parse(
            config.get("end_datetime")).strftime("%Y-%m-%d %H:%M:%S")

    singer.write_schema(tap_stream_id, stream.schema.to_dict(),
                        stream.key_properties)

    keys = {"table": metadata["table"],
            "columns": ".".join(metadata["columns"]),
            "datetime_key": metadata.get("datetime_key"),
            "start_datetime": start_datetime,
            "end_datetime": end_datetime
            }

    query = _build_query(keys, metadata.get("filters", []))
    query_job = client.query(query)

    properties = stream.schema.properties

    LOGGER.info("Running query:\n    %s" % query)
    with metrics.record_counter(tap_stream_id) as counter:
        for row in query_job:
            extract_tstamp = datetime.datetime.utcnow()
            extract_tstamp = extract_tstamp.replace(
                tzinfo=datetime.timezone.utc)

            record = {}
            for key in properties.keys():
                prop = properties[key]

                if key == LEGACY_TIMESTAMP:
                    record[key] = int(round(time.time() * 1000))
                elif key == EXTRACT_TIMESTAMP:
                    record[key] = extract_tstamp.isoformat()
                elif key == BATCH_TIMESTAMP:
                    # This should be written in the target
                    pass
                elif (type(row[key]) == datetime.datetime or
                      type(row[key]) == datetime.date):
                    record[key] = row[key].isoformat()
                else:
                    record[key] = row[key]

            singer.write_record(stream.stream, record)
            last_update = record[keys["datetime_key"]]
            counter.increment()

    state = singer.write_bookmark(state, tap_stream_id, BOOKMARK_KEY_NAME,
                                  last_update)
    singer.write_state(state)
