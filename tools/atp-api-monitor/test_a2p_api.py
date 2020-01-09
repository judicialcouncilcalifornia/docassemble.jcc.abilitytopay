import requests
import json
import sys

from test_a2p_api_config import uat_config, prod_config, sample_citation_params


def test_fetch_citation(env, county, citation_number=None):
    env = env.lower()
    county = county.lower()

    supported_counties = sample_citation_params.keys()
    if county not in supported_counties:
        print('county must be one of [{}], not {}'.format(
            ', '.join(supported_counties), county
        ))
        sys.exit(1)

    if env == 'prod':
        config = prod_config
    else:
        config = uat_config

    params = sample_citation_params.get(county)

    if citation_number is not None:
        params['num'] = citation_number

    access_token = fetch_access_token(config)
    print(access_token, flush=True)

    res = fetch_citation(config, access_token, params)
    print(res.request.url, flush=True)
    print(res.status_code, flush=True)
    return res


def fetch_all_citations(config, access_token, params):
    url = config.get('base_url') + '/case/cases'
    print('Fetching all citations...', flush=True)
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    return requests.post(url, data=None, json=params, headers=headers,
                         timeout=20)


def fetch_citation(config, access_token, params):
    url = config.get('base_url') + '/case/citation'
    print('Fetching citation...', flush=True)
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    return requests.post(url, data=None, json=params, headers=headers,
                         timeout=20)


def fetch_access_token(config):
    resource = config.get('oauth_resource')
    oauth_params = {
        'resource': resource,
        'grant_type': 'client_credentials',
        'client_id': config.get('client_id'),
        'client_secret': config.get('client_secret'),
        'scope': 'openid ' + resource
    }

    print('Fetching access token...', flush=True)
    r = requests.post(config.get('ad_url'), oauth_params, timeout=10)
    data = r.json()
    if 'access_token' not in data:
        print('could not get access token', r, flush=True)
        return

    return data['access_token']
