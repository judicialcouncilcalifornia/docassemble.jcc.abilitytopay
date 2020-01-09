# ATP API Monitor Server + API Test Scripts

This directory contains:

`server.py` - a trivial server that Uptime Robot hits to determine the status of the ATP API
`deploy.sh` - a script for redeploying the above server

`test_a2p_api.py` - a lib with helper functions for hitting the ATP API in exactly the same way as the Docassemble web application

Three different ways to fetch citations from the ATP API:
`fetch_citation_from_number.py`
`fetch_citations_from_name_dob_drivers_license.py`
`fetch_citations_from_number_and_name_dob_drivers_license.py`

## Test scripts example usage

NOTE: You need a `test_a2p_api_config.py` file in order to use any of the scripts in this directory.

```
./fetch_citation_from_number.py uat tulare 1234
./fetch_citations_from_name_dob_drivers_license.py prod "San Francisco" Bob Bobba 1990-11-23 ABC123
./fetch_citations_from_number_and_name_dob_drivers_license.py uat Shasta 1234
```
