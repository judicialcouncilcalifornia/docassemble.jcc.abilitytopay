#!/usr/bin/env python3

import sys
import json
import test_a2p_api
import dateutil.parser

from test_a2p_api_config import uat_config, prod_config


def date_from_iso8601(date_string):
    return dateutil.parser.parse(date_string).date()


if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('Usage: ./fetch_citations_from_number_and_name_dob_drivers_license.py <env> <county> [<citation-number>]')
    sys.exit(1)

env = sys.argv[1]
county = sys.argv[2]
if len(sys.argv) == 4:
    citation_number = sys.argv[3]
else:
    citation_number = None

citation_result = test_a2p_api.test_fetch_citation(
    env, county, citation_number
)
if citation_result.status_code == 200:
    citations = citation_result.json()

    if (type(citations) == dict):
        citations = [citations]

    if len(citations) > 1:
        print('Found {} citations with citation number {}'.format(
            len(citations), citation_number
        ))
        sys.exit(1)

    citation = citations[0]
    print(citation['dateOfBirth'])
    first_name = citation['firstName']
    last_name = citation['lastName']
    dob = date_from_iso8601(citation['dateOfBirth'])
    drivers_license = citation['driversLicense']
    county = citation['county']

    case_params = {
      'firstName': first_name,
      'lastName': last_name,
      'dateOfBirth': dob.isoformat(),
      'driversLicense': drivers_license,
      'county': county
    }

    print(case_params)

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

else:
    print(citation_result.status_code, citation_result.text)
