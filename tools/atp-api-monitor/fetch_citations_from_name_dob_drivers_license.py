#!/usr/bin/env python3

import sys
import json
import test_a2p_api
import dateutil.parser

from test_a2p_api_config import uat_config, prod_config


def date_from_iso8601(date_string):
    return dateutil.parser.parse(date_string).date()


if len(sys.argv) != 7:
    print((
        'Usage: ./fetch_citations_from_name_dob_drivers_license.py '
        '<env> <county> '
        '<first name> <last name> <yyyy-mm-dd> <drivers license>'
    ))
    sys.exit(1)

env = sys.argv[1]
county = sys.argv[2]
first_name = sys.argv[3]
last_name = sys.argv[4]
dob = sys.argv[5]
drivers_license = sys.argv[6]

case_params = {
  'firstName': first_name,
  'lastName': last_name,
  'dateOfBirth': dob,
  'driversLicense': drivers_license,
  'county': county
}

if env == 'prod':
    config = prod_config
else:
    config = uat_config

access_token = test_a2p_api.fetch_access_token(config)

all_citations_result = test_a2p_api.fetch_all_citations(
    config, access_token, case_params
)

if (all_citations_result.status_code == 200):
    print(json.dumps(all_citations_result.json(), indent=4))
else:
    print(all_citations_result.status_code, all_citations_result.text)
