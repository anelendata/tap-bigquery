# tap-bigquery

Reverse ETL: Extract data from BigQuery tables.

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls table data from Google BigQuery
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

## Installation

### Step 1: Activate the Google BigQuery API

 (originally found in the [Google API docs](https://googlecloudplatform.github.io/google-cloud-python/latest/bigquery/usage.html))

 1. Use [this wizard](https://console.developers.google.com/start/api?id=bigquery-json.googleapis.com) to create or select a project in the Google Developers Console and activate the BigQuery API. Click Continue, then Go to credentials.
 1. On the **Add credentials to your project** page, click the **Cancel** button.
 1. At the top of the page, select the **OAuth consent screen** tab. Select an **Email address**, enter a **Product name** if not already set, and click the **Save** button.
 1. Select the **Credentials** tab, click the **Create credentials** button and select **OAuth client ID**.
 1. Select the application type **Other**, enter the name "Singer BigQuery Target", and click the **Create** button.
 1. Click **OK** to dismiss the resulting dialog.
 1. Click the Download button to the right of the client ID.
 1. Move this file to your working directory and rename it *client_secrets.json*.

### Authentication

It is recommended to use `target-bigquery` with a service account.
* Download the client_secrets.json file for your service account, and place it on the machine where `target-bigquery` will be executed.
* Set a `GOOGLE_APPLICATION_CREDENTIALS` environment variable on the machine, where the value is the fully qualified path to client_secrets.json

It should be possible to use the oAuth flow to authenticate to GCP as well:
* `target-bigquery` will attempt to open a new window or tab in your default browser. If this fails, copy the URL from the console and manually open it in your browser.
* If you are not already logged into your Google account, you will be prompted to log in.
* If you are logged into multiple Google accounts, you will be asked to select one account to use for the authorization.
* Click the **Accept** button to allow `target-bigquery` to access your Google BigQuery table.
* You can close the tab after the signup flow is complete.

The data will be written to the table specified in your `config.json`.


## Development Note

Python tap tutorial
https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#a-python-tap

BigQuery Python example
https://cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries#client-libraries-install-python

Use Cookie cutter
https://github.com/cookiecutter/cookiecutter

To create the skeleton for BigQuery tap
https://github.com/singer-io/singer-tap-template


---

Copyright &copy; 2019 Anelen Data
