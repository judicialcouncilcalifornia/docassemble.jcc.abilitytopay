# Ability to Pay DocAssemble Interview

## Local Development Installation

DocAssemble uses Docker for both local development and deployment. You can find the instructions to setup Docassemble using Docker here:

https://docassemble.org/docs/docker.html#install

## Configuration

This is a standard DocAssemble package. The only required configuration is setting up the appropriate A2P API keys in the DocAssemble Configuration tab in the admin dropdown:

    a2p:
      client_id: <client id for backend>
      client_secret: <client secret for backend>
      blob_account_key: <azure storage blob account key>
      oauth_resource: <resource ID for backend>
      base_url: <API host for making requests to A2P backend>
      ad_url: <ActiveDirectory URL for getting oauth tokens>

You can also set the following variables to enable exception emails:

    error notification email: <some email>
    error notification variables: True

To setup email support (so that exception emails will actually send), make sure you have a properly configured SMTP server or provider like SendGrid and follow the steps here: https://docassemble.org/docs/config.html#mail

## TODO

* Insert notes about CSS/styling process
