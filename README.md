[![Build Status](https://travis-ci.com/anelendata/tap-bigquery.svg?branch=master)](https://travis-ci.com/anelendata/tap-bigquery)

# tap-bigquery

Extract data from BigQuery tables.

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls data from Google BigQuery tables/views with datetime field.
- Infers the schema for each resource and produce catalog file.
- Incrementally pulls data based on the input state.

## Installation

### Step 0: Acknowledge LICENSE and TERMS

Please especially note that the author(s) of tap-bigquery is not responsible
for the cost, including but not limited to BigQuery cost) incurred by running
this program.

### Step 1: Activate the Google BigQuery API

 (originally found in the [Google API docs](https://googlecloudplatform.github.io/google-cloud-python/latest/bigquery/usage.html))

 1. Use [this wizard](https://console.developers.google.com/start/api?id=bigquery-json.googleapis.com) to create or select a project in the Google Developers Console and activate the BigQuery API. Click Continue, then Go to credentials.
 2. On the **Add credentials to your project** page, click the **Cancel** button.
 3. At the top of the page, select the **OAuth consent screen** tab. Select an **Email address**, enter a **Product name** if not already set, and click the **Save** button.
 4. Select the **Credentials** tab, click the **Create credentials** button and select **OAuth client ID**.
 5. Select the application type **Other**, enter the name "Singer BigQuery Tap", and click the **Create** button.
 6. Click **OK** to dismiss the resulting dialog.
 7. Click the Download button to the right of the client ID.
 8. Move this file to your working directory and rename it *client_secrets.json*.


Export the location of the secret file:

```
export GOOGLE_APPLICATION_CREDENTIALS="./client_secret.json"
```

For other authentication method, please see Authentication section.

### Step 2: Install

First, make sure Python 3 is installed on your system or follow these 
installation instructions for Mac or Ubuntu.

```
pip install -U tap-bigquery
```

Or you can install the lastest development version from GitHub:

```
pip install --no-cache-dir https://github.com/anelendata/tap-bigquery/archive/master.tar.gz#egg=tap-bigquery
```

## Run

### Step 1: Configure

Create a file called tap_config.json in your working directory, following 
config.sample.json:

```
{
  "streams": [
      {"name": "<some_schema_name>",
       "table": "`<project>.<dataset>.<table>`",
       "columns": ["<col_name_0>", "<col_name_1>", "<col_name_2>"],
       "datetime_key": "<your_key>",
       "filters": ["country='us'", "state='CA'",
                   "registered_on>=DATE_ADD(current_date, INTERVAL -7 day)"
                  ] // also optional: these are parsed in 'WHERE' clause
      }
    ],
  "start_datetime": "2017-01-01T00:00:00Z", // This can be set at the command line argument
  "end_datetime": "2017-02-01T00:00:00Z", // end_datetime is optional
  "limit": 100,
  "start_always_inclusive": false // default is false, optional
}
```

- The required parameters is at least one stream (one bigquery table/view) to copy.
  - It is not a recommended BigQuery practice to use `*` to specify the columns
    as it may blow up the cost for a table with a large number of columns.
  - `filters` are optional but we strongly recommend using this over a large
    partitioned table to control the cost. LIMIT  (The authors of tap-bigquery is not
    responsible for the cost incurred by running this program. Always test
    thoroughly with small data set first.)
- `start_datetime` must also be set in the config file or as the command line
  argument (See the next step).
- `limit` will limit the number of results, but it does not result in reduce
  the query cost.

The table/view is expected to have a column to indicate the creation or
update date and time so the tap sends the query with `ORDER BY` and use
the column to record the bookmark (See State section).

### Step 2: Create catalog

Run tap-bigquery in discovery mode to let it create json schema file and then
run them together, piping the output of tap-bigquery to target-csv:

```
tap-bigquery -c tap_config.json -d > catalog.json
```

### Step 3: Run

tap-bigquery can be run with any Singer Target. As example, let use
[target-csv](https://github.com/singer-io/target-csv).

```
pip install target-csv
```

Run:

```
tap-bigquery -c tap_config.json \
    --catalog catalog.json --start_datetime '2020-08-01T00:00:00Z' \
    --end_datetime '2020-08-02T01:00:00Z' | target-csv --config target_config.json \
    > state.json
```

This example should create a csv file in the same directory.
`state.json` should contain a state (bookmark) after the run. (See State section).

Notes:

- start and end datetimes accept ISO 8601 format, can be date only. start datetime
  is inclusive, end datetime is not.
- It is recommended to inspect the catalog file and fix the auto-type assignment
  if necessary.
- target-csv's target_config.json is optinal.
- tap-bigquery can produce nested records but it's up to target if the data
  writing will be successful. In this example with target-csv, the table is
  expected to be flat.

## Authentication

It is recommended to use `tap-bigquery` with a service account.

- Download the client_secrets.json file for your service account, and place it
  on the machine where `tap-bigquery` will be executed.
- Set a `GOOGLE_APPLICATION_CREDENTIALS` environment variable on the machine,
  where the value is the fully qualified path to client_secrets.json

In the testing environment, you can also manually authenticate before runnig
the tap. In this case you do not need `GOOGLE_APPLICATION_CREDENTIALS` defined:

```
gcloud auth application-default login
```

You may also have to set the project:

```
gcloud config set project <project-id>
```

Though not tested, it should also be possible to use the OAuth flow to
authenticate to GCP as well:
- `tap-bigquery` will attempt to open a new window or tab in your default
  browser. If this fails, copy the URL from the console and manually open it
  in your browser.
- If you are not already logged into your Google account, you will be prompted
  to log in.
- If you are logged into multiple Google accounts, you will be asked to select
  one account to use for the authorization.
- Click the **Accept** button to allow `tap-bigquery` to access your Google BigQuery
  table.
- You can close the tab after the signup flow is complete.

## State

This tap emits [state](https://github.com/singer-io/getting-started/blob/master/docs/CONFIG_AND_STATE.md#state-file).
The command also takes a state file input with `--state <file-name>` option.
If the state is set, start_datetime config and command line argument are
ignored and the datetime value from last_update key is used as the resuming
point.

To avoid the data duplication, start datetime is exclusive
`start_datetime < datetime_column` when the tap runs with state option. If
you fear a data loss because of this, just use the `--start_datetime` option
instead of state. Or set `start_always_inclusive: true` in configuration.

The tap itself does not output a state file. It anticipate the target program
or a downstream process to fianlize the state safetly and produce a state file.

## Original repo
https://github.com/anelendata/tap-bigquery

Copyright &copy; 2020- Anelen Data
