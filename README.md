# tap-bigquery

Reverse ETL: Extract data from BigQuery tables.

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls table data from Google BigQuery
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

## Installation

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
 
### Step 2: Configure

Create a file called config.json in your working directory, following config.sample.json. The required parameters are the start_datetime and at least one stream (one bigquery table) to copy.

### Step 3: Install and Run

First, make sure Python 3 is installed on your system or follow these installation instructions for Mac or Ubuntu.

tap-bigquery can be run with any Singer Target. As example, let use target-redshift

These commands will install target-redshift and tap-bigquery with pip. Export google client secrets file to auth in Google cloud. Run tap-bigquery in discovery mode to let it create json schema file and then run them together, piping the output of tap-bigquery to target-redshift:

```
> pip install tap-bigquery pipelinewise-target-redshift

> export GOOGLE_APPLICATION_CREDENTIALS="./client_secret.json"

> tap_bigquery -c config.json -d > catalog.json

> tap_bigquery -c config.json --catalog catalog.json --start_datetime '2020-05-01T00:00:00Z' --end_datetime '2020-05-01T01:00:00Z'
```

### Authentication

It is recommended to use `tap-bigquery` with a service account.
* Download the client_secrets.json file for your service account, and place it on the machine where `tap-bigquery` will be executed.
* Set a `GOOGLE_APPLICATION_CREDENTIALS` environment variable on the machine, where the value is the fully qualified path to client_secrets.json

It should be possible to use the oAuth flow to authenticate to GCP as well:
* `tap-bigquery` will attempt to open a new window or tab in your default browser. If this fails, copy the URL from the console and manually open it in your browser.
* If you are not already logged into your Google account, you will be prompted to log in.
* If you are logged into multiple Google accounts, you will be asked to select one account to use for the authorization.
* Click the **Accept** button to allow `tap-bigquery` to access your Google BigQuery table.
* You can close the tab after the signup flow is complete.

The data will be written to the table specified in your `config.json`.


## Original repo
https://github.com/anelendata/tap_bigquery

Copyright &copy; 2019 Anelen Data
