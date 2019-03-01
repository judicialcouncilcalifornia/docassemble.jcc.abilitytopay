# Ability to Pay DocAssemble Interview

## Local Development Installation

DocAssemble uses Docker for both local development and deployment. You can find the instructions to setup Docassemble using Docker here:

https://docassemble.org/docs/docker.html#install

## Configuration

You can also set the following variables to enable exception emails:

    error notification email: <some email>
    error notification variables: True

This will send an email to the address specified when an error occurs.

## A2P API

### Overview

The file `a2papi.py` contains all the logic to connect to the A2P backend. 

The first step is to acquire an OAuth access token - see below for configuration. We issue a request for a token in the `__do_request` method, and use that token for subsequent requests.

Once we have the access token, we use one of the three main methods: 

* `fetch_citation_data`: Citation-number search against `/case/citation` using citation number and county.
* `fetch_case_data`: Runs a case-based search against the `/case/cases` endpoint using first name, last name, county, license number, and DOB.
* `submit_interview`: Submits the a JSON version of the DA interview to the A2P backend using a custom JSON format. This function also persists any uploaded proof documents to the Blob Storage account on Azure (see below for configuration).

### Configuration

The only required configuration is setting up the appropriate A2P API keys in the DocAssemble Configuration tab in the admin dropdown:

    a2p:
      client_id: <client id for backend>
      client_secret: <client secret for backend>
      blob_account_key: <azure storage blob account key>
      oauth_resource: <resource ID for backend>
      base_url: <API host for making requests to A2P backend>
      ad_url: <ActiveDirectory URL for getting oauth tokens>

To setup email support (so that exception emails will actually send), make sure you have a properly configured SMTP server or provider like SendGrid and follow the steps here: https://docassemble.org/docs/config.html#mail

### Debugging

In situations where results are not ideal, you can view the DocAssemble logs (see here for more info): https://docassemble.org/docs/errors.html

Since we are currently pre-launch, we are debugging the entire request and response objects (including URL, body, headers, and response code). This information is present in the logs to ease with the debugging process.

We also wrap each of the three main entrypoint methods mentioned above in a `try... except` block and send an empty response back to DA. This is to avoid having the user see an unhelpful technical error screen. In the logs, however, we log the exception so that we can debug later (the error begins with the text "Error trying to communicate with A2P API").

## Infrastructure

The DA Ability to Pay instance currently runs on JCC Azure. The setup instructions are located in `infra/azure_notes.sh`.
