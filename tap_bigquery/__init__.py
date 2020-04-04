#!/usr/bin/env python3
import argparse, attr, backoff, datetime, itertools, json, logging, os, pytz, requests, sys, time, urllib

import singer
from singer import utils, metadata
from singer.catalog import Catalog

from . import sync_bigquery as source


REQUIRED_CONFIG_KEYS = ["streams"]

logging.basicConfig(stream=sys.stdout,
                    format="%(asctime)s - " + str(__name__) + " - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
LOGGER = logging.getLogger(__name__)


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
    for stream in catalog.streams:
        stream_metadata = metadata.to_map(stream.metadata)
        # stream metadata will have an empty breadcrumb
        if metadata.get(stream_metadata, (), "selected"):
            selected_streams.append(stream.tap_stream_id)

    return selected_streams

def sync(config, state, catalog):

    selected_stream_ids = get_selected_streams(catalog)

    # Loop over streams in catalog
    for stream in catalog.streams:
        stream_id = stream.tap_stream_id
        stream_schema = stream.schema
        if stream_id in selected_stream_ids:
            source.do_sync(config, stream)
            LOGGER.info('Syncing stream:' + stream_id)
    return


def parse_args(required_config_keys):
    ''' This is to replace singer's default utils.parse_args()
    https://github.com/singer-io/singer-python/blob/master/singer/utils.py

    Parse standard command-line args.
    Parses the command-line arguments mentioned in the SPEC and the
    BEST_PRACTICES documents:
    -c,--config     Config file
    -s,--state      State file
    -d,--discover   Run in discover mode
    -p,--properties Properties file: DEPRECATED, please use --catalog instead
    --catalog       Catalog file
    Returns the parsed args object from argparse. For each argument that
    point to JSON files (config, state, properties), we will automatically
    load and parse the JSON file.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-s', '--state',
        help='State file')

    parser.add_argument(
        '-p', '--properties',
        help='Property selections: DEPRECATED, Please use --catalog instead')

    parser.add_argument(
        '--catalog',
        help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')

    # Capture additional args
    parser.add_argument(
        "--start_datetime", type=str, default=None,
        help="Inclusive start date time in ISO8601-Date-String format: 2019-04-11T00:00:00Z")
    parser.add_argument(
        "--end_datetime", type=str, default=None,
        help="Exclusive end date time in ISO8601-Date-String format: 2019-04-12T00:00:00Z")

    args = parser.parse_args()
    if args.config:
        args.config = utils.load_json(args.config)
    if args.state:
        args.state = utils.load_json(args.state)
    else:
        args.state = {}
    if args.properties:
        args.properties = utils.load_json(args.properties)
    if args.catalog:
        args.catalog = Catalog.load(args.catalog)

    utils.check_config(args.config, required_config_keys)

    return args


@utils.handle_top_exception(LOGGER)
def main():
    args = parse_args(REQUIRED_CONFIG_KEYS)
    CONFIG.update(args.config)

    # Overwrite config specs with commandline args if present
    if args.start_datetime:
        CONFIG["start_datetime"] = args.start_datetime
    if args.end_datetime:
        CONFIG["end_datetime"] = args.end_datetime

    if not CONFIG.get("end_datetime"):
        CONFIG["end_datetime"]  = datetime.datetime.utcnow().isoformat()

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover(CONFIG)
        print(json.dumps(catalog, indent=2))
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = Catalog.from_dict(discover(CONFIG))

        sync(CONFIG, args.state, catalog)


CONFIG = {}
for key in REQUIRED_CONFIG_KEYS:
    CONFIG[key] = None

if __name__ == "__main__":
    main()
