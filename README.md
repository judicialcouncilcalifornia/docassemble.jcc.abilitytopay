# Ability to Pay DocAssemble Interview

## Setup

This is a standard DocAssemble package. The only required configuration is setting up the appropriate A2P API keys in the DocAssemble Configuration tab in the admin dropdown:

    a2p:
      client_id: <client id for backend>
      client_secret: <client secret for backend>
      blob_account_key: <azure storage blob account key>
      oauth_resource: <resource ID for backend>
      base_url: <API host for making requests to A2P backend>
      ad_url: <ActiveDirectory URL for getting oauth tokens>

## TODO

* Insert notes about CSS/styling process
