# Ability to Pay DocAssemble Interview

[![Build Status](https://travis-ci.com/JudicialCouncilOfCalifornia/docassemble.jcc.abilitytopay.svg?branch=master)](https://travis-ci.com/JudicialCouncilOfCalifornia/docassemble.jcc.abilitytopay)

Ability to Pay is a web application for requesting fine reductions for traffic violations in California counties. It is built with the open source [DocAssemble](https://docassemble.org/) framework.

## Directory Structure

```
- docassemble
-- jcc
--- abilitytopay

---- a2papi.py (core python module for interacting with ATP API, error-handling, etc.)
---- a2putil.py
---- templates.py (HTML snippets)
---- translations.py (all interview text lives here in both English + Spanish)

---- data (python source code)
----- es-words.yml (Spanish translations for "system" words)
----- questions (ymls that describe each interview question, with some embedded python logic)
----- static (static assets)

- infra (READMEs for maintaining + deploying new instances of the webapp)
- source (sass stylesheets that get built into css)
- tests
- tools
```

## Development

The development environment is deployed to https://mycitations.dev.courts.ca.gov. Since Docassemble runs in a container, developing locally is not any easier than developing in the dev environment. However, if you want to develop locally, see [Developing on a local machine](#Developing-on-a-local-machine).

### Install development dependencies

```
npm install --only=dev
```

### Building CSS from SASS

SASS is CSS with some extra syntax sugar that makes stylesheets easier to maintain. The stylesheets in this project are written in SASS in the [source/](source/) directory and compiled to CSS.

Run

```
npm run build
```

to compile the `.scss` files in [source/](source/) into `.css` files in [docassemble/jcc/abilitytopay/data/static/](docassemble/jcc/abilitytopay/data/static/).

This is the only build step--all other source files are edited in-place in the [docassemble/jcc/abilitytopay](docassemble/jcc/abilitytopay) package directory.

### Versioning

See [write_version.py](write_version.py) and the version scripts in [package.json](package.json). Use the npm version commands to bump the version. E.g.:

```
npm version minor
```

This will:
- bump the version in package.json and package-lock.json
- write the new version to [version.js](docassemble/jcc/abilitytopay/data/static/version.js) (which gets loaded by the webapp)
- commit the above 2 changes and tag the commit with the new version number

At this point, if you made a mistake, you can `git tag -d <version-number-goes-here>` (e.g. `git tag -d v1.0.2`) to delete the version tag and `git reset HEAD~1 --hard` to undo the version commit.

If you did everything right, push the version commit and tag:

```
git push && git push --tags
```

### Developing on a local machine

DocAssemble uses Docker for both local development and deployment. You can find the instructions to setup Docassemble using Docker here:

https://docassemble.org/docs/docker.html#install

Once DocAssemble is running, visit the admin page at e.g. http://localhost:8080/updatepackage, create a user account, and install this repo as a package.

## A2P API

### Overview

[a2papi.py](docassemble/jcc/abilitytopay/a2papi.py) contains all the logic to connect to the A2P backend. 

The first step is to acquire an OAuth access token - see below for configuration. We issue a request for a token in each call to `__do_request`.

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
      blob_account_name: <azure storage blob account name>
      oauth_resource: <resource ID for backend>
      base_url: <API host for making requests to A2P backend>
      ad_url: <ActiveDirectory URL for getting oauth tokens>

You'll also want to set the default interview:

    default interview: docassemble.jcc.abilitytopay:data/questions/interview.yml

You can also set the following variables to enable exception emails:

    error notification email: <some email>
    error notification variables: True

This will send an email to the address specified when an error occurs.

To setup email support (so that exception emails will actually send), make sure you have a properly configured SMTP server or provider like SendGrid and follow the steps here: https://docassemble.org/docs/config.html#mail

### Debugging

In situations where results are not ideal, you can view the DocAssemble logs (see here for more info): https://docassemble.org/docs/errors.html

Since we are currently pre-launch, we are debugging the entire request and response objects (including URL, body, headers, and response code). This information is present in the logs to ease with the debugging process.

We also wrap each of the three main entrypoint methods mentioned above in a `try... except` block and send an empty response back to DA. This is to avoid having the user see an unhelpful technical error screen. In the logs, however, we log the exception so that we can debug later (the error begins with the text "Error trying to communicate with A2P API").

#### More DocAssemble logs

From https://docassemble.org/docs/docker.html#troubleshooting:

Log files on the container that you might wish to check include:

- /var/log/supervisor/initialize-stderr---supervisor-*.log (log for the startup process)
- /var/log/supervisor/postgres-stderr---supervisor-*.log (log for the SQL server)
- Other files in /var/log/supervisor/ (logs for other services)
- /var/log/apache2/error.log (log for the web server)
- /usr/share/docassemble/log/docassemble.log (log for the web application)
- /usr/share/docassemble/log/worker.log (log for background processes)
- /var/mail/mail (log for scheduled tasks, generated by cron)
- /tmp/flask.log (log used by Flask in rare situations)

#### Entering Docassemble's python virtualenv

From within the docassemble container:

```
su www-data
source /usr/share/docassemble/local3.5/bin/activate
```

#### Inspecting the Docassemble database:

From within the docassemble container:

```
psql -U docassemble -d docassemble -h localhost -W
abc123
```

### Infrastructure

The DA Ability to Pay instance currently runs on JCC Azure. The setup instructions are located in [infra/README.md](infra/README.md).

Since DA does not maintain tagged Docker releases, we maintain our own fork that we regularly update at `rdeshpande/docassemble`. Update the docker image by running:

    ./rebuild_docker_image.sh

### Deployment

This application is currently deployed to:
- https://mycitations.uat.courts.ca.gov/ for testing
- https://mycitations.courts.ca.gov/ for production

This repository is installed as a package in both deployments. The testing deployment installs from the [uat branch](https://github.com/JudicialCouncilOfCalifornia/docassemble.jcc.abilitytopay/tree/uat), and the production deployment installs from the [prod branch](https://github.com/JudicialCouncilOfCalifornia/docassemble.jcc.abilitytopay/tree/prod).

To update deployed code, push to the corresponding branch, then visit e.g. https://mycitations.uat.courts.ca.gov/updatepackage, scroll down to the docassemble.jcc.abilitytopay package, and click "update".

#### Monitoring

The testing and production deployments are monitored with [UptimeRobot](https://uptimerobot.com/). The monitor is configured to look for the words:

```
Request a Fine Reduction
```

on the two courts.ca.gov pages linked above. The monitor sends an e-mail when a service goes up or down.
