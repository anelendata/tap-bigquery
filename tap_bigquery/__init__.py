#!/usr/bin/env python3
import os
import json
import singer
from singer import utils, metadata

from . import sync_bigquery as source


REQUIRED_CONFIG_KEYS = ["start_date", "username", "password", "streams"]

LOGGER = singer.get_logger()

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

# Load schemas from schemas folder
def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas

def discover(config):
    # raw_schemas = load_schemas()
    streams = []

    for stream in config["streams"]:
    # for schema_name, schema in raw_schemas.item
        stream_metadata, stream_key_properties, schema = source.do_discover(stream)

        # create and add catalog entry
        catalog_entry = {
            'stream': stream["name"],
            'tap_stream_id': stream["name"],
            'schema': schema,
            'metadata' : stream_metadata,
            'key_properties': stream_key_properties
        }
        streams.append(catalog_entry)

    return {'streams': streams}

def get_selected_streams(catalog):
    '''
    Gets selected streams.  Checks schema's 'selected' first (legacy)
    and then checks metadata (current), looking for an empty breadcrumb
    and mdata with a 'selected' entry
    '''
    selected_streams = []
    for stream in catalog["streams"]:
        stream_metadata = metadata.to_map(stream["metadata"])
        # stream metadata will have an empty breadcrumb
        if metadata.get(stream_metadata, (), "selected"):
            selected_streams.append(stream["tap_stream_id"])

    return selected_streams

def sync(config, state, catalog):

    selected_stream_ids = get_selected_streams(catalog)

    # Loop over streams in catalog
    for stream in catalog["streams"]:
        stream_id = stream["tap_stream_id"]
        stream_schema = stream["schema"]
        if stream_id in selected_stream_ids:
            source.do_sync(stream)
            LOGGER.info('Syncing stream:' + stream_id)
    return

@utils.handle_top_exception(LOGGER)
def main():

    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover(args.config)
        print(json.dumps(catalog, indent=2))
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog =  discover(args.config)

        sync(args.config, args.state, catalog)


CONFIG = {}
for key in REQUIRED_CONFIG_KEYS:
    CONFIG[key] = None

if __name__ == "__main__":
    main()
