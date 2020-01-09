#!/usr/bin/env python3

import json
import test_a2p_api
import sys

if len(sys.argv) < 3 or len(sys.argv) > 4:
    print('Usage: ./fetch_citation_from_number.py <env> <county> [<citation-number>]')
    sys.exit(1)

env = sys.argv[1]
county = sys.argv[2]
if len(sys.argv) == 4:
    citation_number = sys.argv[3]
else:
    citation_number = None

result = test_a2p_api.test_fetch_citation(env, county, citation_number)
if result.status_code == 200:
    print(json.dumps(result.json(), indent=4))
else:
    print(result.status_code, result.text)
