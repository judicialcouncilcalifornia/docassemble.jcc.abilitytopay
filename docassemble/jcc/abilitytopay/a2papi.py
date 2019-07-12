import calendar
import datetime
import hashlib
import json
import re
import time
import requests
from azure.storage.blob import BlockBlobService
from docassemble.base.util import *
from .a2putil import date_from_iso8601, format_money



def fetch_case_data_from_citation(citation_number, county):
    try:
        # fetch citation data
        citation_response = fetch_citation_data(citation_number, county)
        citation = citation_response['data']
    except Exception as e:
        return __error_response(e)        

    try:
        # pull info out of citation result
        first_name = citation.get('firstName')
        last_name = citation.get('lastName')
        dob = date_from_iso8601(citation.get('dateOfBirth'))
        drivers_license = citation.get('driversLicense')
        county = citation.get('county')
        
        # fetch case data
        case_data = fetch_case_data(first_name, last_name, dob, drivers_license, county)
        return case_data
    except Exception as e:
        # TODO: Send e-mail notification to dev team
        log("Error fetching case data from citation result: %s" % e)

        # If unable to fetch case data from the citation,
        # return a case containing only the original citation.

        # TODO: Use CaseResult and CitationResult classes to clarify the
        # data shapes expected by the frontend
        case_result = citation_response
        case_result['data'] = [citation]
        return case_result


def fetch_citation_data(citation_number, county):
    try:
        citation_params = {
            'num': citation_number,
            'county': county
        }
        res = __do_request(a2p_config()['citation_lookup_url'], citation_params)
        res = __format_response(res)

        if res['data'] is None:
            return res

        # Old API returns a single dict. Wrap it in a list to make it
        # look like the new API. Delete this hunk once new API is deployed and tested.
        if type(res['data']) is dict:
            res['data'] = [res['data']]

        for citation in res['data']:
            citation['eligible'] = __is_citation_eligible(citation)
        return res
    except Exception as e:
        return __error_response(e)


def fetch_case_data(first_name, last_name, dob, drivers_license, county):
    try:
        case_params = {
            'firstName': first_name,
            'lastName': last_name,
            'dateOfBirth': "%s/%s/%s" % (dob.month, dob.day, dob.year),
            'driversLicense': drivers_license,
            'county': county
        }
        res = __do_request(a2p_config()['case_lookup_url'], case_params)
        res = __format_response(res)

        # Only return eligible citations. TODO: Move this logic somewhere else.
        if res['data'] is not None:
            eligible_citations = [citation for citation in res['data'] if __is_citation_eligible(citation)]
            if len(eligible_citations) > 0:
                res['data'] = eligible_citations
            else:
                res['data'] = None
        return res
    except Exception as e:
        return __error_response(e)


def submit_interview(data, attachments=[], debug=False):
    try:
        params = __build_submit_payload_and_upload_images(data, attachments)
        res = __do_request(a2p_config()['submit_url'], params)

        if debug:
            return __format_response(res, params)
        else:
            return __format_response(res)
    except Exception as e:
        return __error_response(e)


def __format_response(response, request_body=None):
    response_data = {}
    response_data['response_code'] = response.status_code
    response_data['data'] = response.json()

    # Protect against server response of empty hash
    if response_data['data'] == [{}] or response_data['data'] == {}:
        response_data['data'] = None

    if response.ok:
        response_data['success'] = True
        response_data['error'] = None

        if request_body:
            response_data['request_body'] = request_body
    else:
        response_data['data'] = None
        response_data['success'] = False
        response_data['error'] = response.text

    return response_data


def __log_response(msg, response):
    lines = []
    lines.append("-----------")
    lines.append(msg)
    lines.append("Request URL: %s" % response.request.url)
    lines.append("Request Body: %s" % response.request.body)
    lines.append("Request Headers: %s" % response.request.headers)
    lines.append("Response URL: %s" % response.url)
    lines.append("Response Body: %s" % response.text)
    lines.append("Response Headers: %s" % response.headers)
    lines.append("Response Code: %s" % response.status_code)
    lines.append("-----------")
    for line in lines:
        log(line)


def __do_request(url, params):
    resource = a2p_config()['oauth_resource']
    oauth_params = {
        'resource': resource,
        'grant_type': 'client_credentials',
        'client_id': a2p_config()["client_id"],
        'client_secret': a2p_config()["client_secret"],
        'scope': 'openid ' + resource
    }
    r = requests.post(a2p_config()["ad_url"], oauth_params, timeout=10)
    data = r.json()
    if 'access_token' not in data:
        __log_response("could not get access token", r)

    access_token = data['access_token']

    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    res = requests.post(url, data=None, json=params, headers=headers, timeout=30)
    __log_response("a2p api request", res)
    return res


def a2p_config():
    cfg = get_config('a2p')
    base_url = cfg['base_url']
    cfg['citation_lookup_url'] = base_url + '/case/citation'
    cfg['case_lookup_url'] = base_url + '/case/cases'
    cfg['submit_url'] = base_url + '/request'
    return cfg


def __submit_image_from_url(proof_type, url):
    # TODO: Find a better way to get original filename from DA.
    filename = "ProofOf%s" % proof_type
    try:
        orig_filename = re.findall(r"filename%3D(.*?)(&|$)", url)[0][0]
        filename += "_%s" % orig_filename
    except:
        pass

    blob_service = BlockBlobService(account_name=a2p_config()['blob_account_name'], account_key=a2p_config()['blob_account_key'])
    image_body = requests.get(url).content
    blob_service.create_blob_from_bytes('attachments', filename, image_body)

    return {
        "fileName": filename,
        "blobName": filename,
        "size": len(image_body)
    }


def __build_submit_payload_and_upload_images(data, attachments):
    benefit_files_data = []

    for proof_type, url in attachments:
        log("Uploading file: %s" % url)
        image_meta = __submit_image_from_url(proof_type, url)
        benefit_files_data.append(image_meta)

    proof_fields = [
        'calfresh',
        'medi_cal',
        'ssi',
        'ssp',
        'cr_ga',
        'ihss',
        'tanf'
        'cal_works',
        'wic',
        'capi',
    ]

    no_docs_upload_comments = []
    for field in proof_fields:
        reason = data.get(field + "_no_proof_reason")
        if reason:
            no_docs_upload_comments.append("%s: %s" % (field, reason))

    case_information = data.get('case_information')

    benefits = data.get('benefits', {}).get('elements', {})
    no_benefits = True
    for benefit_name in ['cal_fresh', 'ssi', 'ssp', 'medi_cal', 'cr_ga', 'ihss', 'cal_works', 'wic', 'tanf', 'capi', 'other']:
        if benefits.get(benefit_name):
            no_benefits = False

    submitted_on = datetime.datetime.now().isoformat()

    on_other_benefits = benefits.get('other', False)
    other_benefits_desc = None
    if on_other_benefits:
        other_benefits_desc = data.get('other_benefit_name')
        no_benefits = False

    violDescriptions = []
    idx = 0
    for charge in case_information.get('charges', {}):
        descr = []
        idx += 1
        descr.append("Count %s" % idx)
        if charge.get('chargeCode'):
            descr.append(charge.get('chargeCode'))
        descr.append(charge.get('violationDescription'))
        violDescriptions.append("-".join(descr))

    additional_requests = data.get('additional_requests', {}).get('elements', {})

    difficultyToVisitCourtDueTo = data.get("difficult_open_text", "")
    for k, v in data.get('why_difficult', {}).get('elements', {}).items():
        if v:
            difficultyToVisitCourtDueTo += "/ " + k

    other_expenses = []
    hardship_desc = data.get('hardship')
    hardship_amt = data.get('hardship_amt')

    # We only check for the description in case the amount is blank.
    # The A2P team confirmed a null value for the amount is OK.
    # We need to send an empty array if no extra hardship is provided.
    if hardship_desc:
        other_expenses.append({
            'otherExpensesDesc': hardship_desc,
            'otherExpensesAmt': hardship_amt,
        })

    hasCivilAssessFee = case_information.get('civilAssessFee', 0) > 0

    request_params = {
        "requestStatus": "Submitted",
        "petition": {
            "noBenefits": no_benefits,
            "onFoodStamps": benefits.get('cal_fresh', False),
            "onSuppSecIncome": benefits.get('ssi', False),
            "onSSP": benefits.get('ssp', False),
            "onMedical": benefits.get('medi_cal', False),
            "onCountyRelief": benefits.get('cr_ga', False),
            "onIHSS": benefits.get('ihss', False),
            "onCalWorks": benefits.get('cal_works', False),
            # Don't send WIC info to backend until backend supports WIC
            # "onWIC": benefits.get('wic', False),
            "onTANF": benefits.get('tanf', False),
            "onCAPI": benefits.get('capi', False),
            "benefitFiles": benefit_files_data,
            "rent": data.get('monthly_rent'),
            "mortgage": data.get('mortgage'),
            "phone": data.get('phone_bill'),
            "food": data.get('food'),
            "insurance": data.get('insurance'),
            "isBenefitsProof": len(attachments) == 0,
            "isCivilAssessWaiver": False,
            "clothes": data.get('clothing'),
            "childSpousalSupp": data.get('child_spousal_support'),
            "carPayment": data.get('transportation'),
            "utilities": data.get('utilities'),
            "otherExpenses": other_expenses,
            "isMoreTimeToPay": additional_requests.get('extension', False),
            "isPaymentPlan": additional_requests.get('payment_plan', False),
            "isReductionOfPayment": True,
            "isCommunityService": additional_requests.get('community_service', False),
            "isOtherRequest": False,
            "otherRequestDesc": data.get('other_hardship'),
            "selectAllRights": True,
            "representByAttorneyRight": True,
            "speedyTrialRight": True,
            "presentEvidenceRight": True,
            "testifyUnderOathRight": True,
            "remainSilentRight": True,
            "isPleadGuilty": data.get('plea', '') == "agree_guilty",
            "isPleadNoContest": data.get('plea', '') == "agree_no_contest",
            "supportingFiles": [],
            "noDocsToUploadReason": "See comments",
            "noDocsToUploadComments": "\n".join(no_docs_upload_comments),
            "isDeclare": True,
            "onOtherBenefits": on_other_benefits,
            "onOtherBenefitsDesc": other_benefits_desc,
        },
        "caseInformation": {
            "caseNumber": case_information.get('caseNumber'),
            "citationDocumentId": case_information.get('documentid'),
            "citationNumber": case_information.get('citationNumber'),
            "civilAssessFee": hasCivilAssessFee,
            "county": data.get('county'),
            "fullName": case_information.get('firstName', '') + ' ' + case_information.get('lastName', ''),
            "totalDueAmt": case_information.get('totalDueAmt'),
            "violationDate": case_information.get('charges', [])[0].get('violationDate'),
            "violationDescription": "\n".join(violDescriptions),

        },
        "benefitsStatus": not no_benefits,
        "defendantInformation": {
            "incomeAmount": data.get('income'),
            "incomeFrequency": "Month",
            "totalFamilyMembers": data.get('residents'),
        },
        "survey": {
            "isAddressedTrafficMatter": data.get('tool_helpful', '') + ',' + data.get('tool_difficult', ''),
            "willYouVisitCourt": data.get('prefer'),
            "difficultyToVisitCourtDueTo": difficultyToVisitCourtDueTo,
        },
        "submittedById": "0",
        "judgment": "Submitted",
        "submittedByEmail": data.get('email_address'),
        "submittedOn": submitted_on,
        "needMoreInformation": [],
        "toolRecommendations": [],
        "judicialOrder": [],
        "auditInformation": [],
        "__v": 0
    }
    return request_params


def __error_response(exception):
    log("Error trying to communicate with A2P API: %s" % exception)
    return {
        'data': None,
        'error': exception,
        'success': False,
    }


def __is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def __is_citation_eligible(data):
    if 'totalDueAmt' not in data:
        return False

    if not __is_number(data['totalDueAmt']):
        return False

    if int(data['totalDueAmt']) == 0:
        return False

    return True

# NOTE: Testing the below functions on local may not work
# due to firewall restrictions.
#
# print(fetch_citation_data('MCRDINTR180000001001', 'Shasta'))
# print(fetch_case_data('john', 'doe', '11/26/1985', '12345', 'Santa Clara'))
# print(submit_interview({ 'citationNumber': 1234 }))
