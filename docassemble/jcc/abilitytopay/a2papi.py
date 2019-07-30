import traceback
import calendar
import datetime
import hashlib
import json
import re
import requests
from azure.storage.blob import BlockBlobService
from docassemble.base.util import *
from .a2putil import date_from_iso8601, format_money

# 
# Exports
# - This is the public interface exported by this module.
# - Only the names listed in __all__ are available to the interview code.
# 

__all__ = [
    'fetch_case_data_from_citation',
    'fetch_case_data',
    'submit_all_citations'
]

# 
# Logging
# 

import time
import logging
import docassemble.base.logger

sys_logger = logging.getLogger('docassemble')

def log_message_with_timestamp(message):
    sys_logger.debug(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message)

# Override the default docassemble logger, which annoyingly strips newlines.
docassemble.base.logger.set_logmessage(log_message_with_timestamp)

# 
# API
# 

def fetch_case_data_from_citation(citation_number, county):
    try:
        # fetch citation data
        citation_response = fetch_citation_data(citation_number, county)
        num_citations = len(citation_response.data)
        if num_citations == 1:
            # Perfect. We received exactly one citation.
            citation = citation_response.data[0]
        if num_citations > 1:
            # No good. We received multiple citations, but we only wanted one. Need to
            # direct user to provide more info to disambiguate.
            return ErrorResult('too-many-results')
        elif num_citations == 0:
            # No citations matched this citation number.
            return SuccessResult(None)
    except Exception as e:
        return ErrorResult(traceback.format_exc())

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

        try:
            # If unable to fetch case data from the citation,
            # return a case containing only the original citation (if eligible).
            if __is_citation_eligible(citation):
                return SuccessResult([citation])
            else:
                return SuccessResult(None)

            # TODO: Use CaseResult and CitationResult classes to clarify the
            # data shapes expected by the frontend
        except Exception as e:
            return ErrorResult(traceback.format_exc())


def fetch_citation_data(citation_number, county):
    try:
        citation_params = {
            'num': citation_number,
            'county': county
        }
        res = __do_request(a2p_config()['citation_lookup_url'], citation_params)
        res = APIResult.from_http_response(res)

        if res.data is None:
            return res

        # Old API returns a single dict. Wrap it in a list to make it
        # look like the new API. Delete this hunk once new API is deployed and tested.
        if type(res.data) is dict:
            res.data = [res.data]

        for citation in res.data:
            citation['eligible'] = __is_citation_eligible(citation)
        return res
    except Exception as e:
        return ErrorResult(traceback.format_exc())


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
        res = APIResult.from_http_response(res)

        # Only return eligible citations. TODO: Move this logic somewhere else.
        if res.data is not None:
            eligible_citations = [citation for citation in res.data if __is_citation_eligible(citation)]
            if len(eligible_citations) > 0:
                res.data = eligible_citations
            else:
                res.data = None
        return res
    except Exception as e:
        return ErrorResult(traceback.format_exc())


def submit_all_citations(data, attachments=[]):
    try:
        # Upload all attachments to blob storage
        benefit_files_data = __upload_images(attachments)
        
        # Submit petition requests one at a time
        submission_results = {}
        for citation in data['selected_citations']:
            citation_number = citation['citationNumber']
            petitioner_payload = __complete_payload(data, benefit_files_data, citation)
            try:
                submission_results[citation_number] = __do_request(a2p_config()['submit_url'], petitioner_payload)
            except Exception as e:
                submission_results[citation_number] = ErrorResult(traceback.format_exc())
        return SuccessResult(submission_results)
    except Exception as e:
        return ErrorResult(traceback.format_exc())


def submit_interview(data, attachments=[]):
    try:
        params = __build_submit_payload_and_upload_images(data, attachments)
        res = __do_request(a2p_config()['submit_url'], params)
        return APIResult.from_http_response(res)
    except Exception as e:
        return ErrorResult(traceback.format_exc())


class APIResult():
    def __init__(self, success, data, error):
        self.success = success
        self.data = data
        self.error = error

    @staticmethod
    def from_http_response(response):
        data = response.json()

        # The API responds with an empty dict instead of null or None
        if (data == [{}]) or (data == {}):
            data = None

        if response.ok:
            return SuccessResult(data)
        else:
            return ErrorResult(response.text)

class SuccessResult(APIResult):
    def __init__(self, data):
        self.success = True
        self.error = None
        self.data = data

class ErrorResult(APIResult):
    def __init__(self, error):
        log("Error trying to communicate with A2P API: %s" % error)
        self.success = False
        self.error = error
        self.data = None


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
    log('\n'.join(lines))


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
    """Uploads an image to an azure blob storage instance that is also accessible by
    the clerk's module. Seems like a strange architectural decision--the A2P API should
    accept the image data as part of the user's submission."""
    
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


def __upload_images(attachments):
    benefit_files_data = []
    for proof_type, url in attachments:
        log("Uploading file: %s" % url)
        image_meta = __submit_image_from_url(proof_type, url)
        benefit_files_data.append(image_meta)
    return benefit_files_data


def __complete_payload(data, benefit_files_data, citation_data):
    payload = __petitioner_payload_without_case_info(data, benefit_files_data)
    payload['caseInformation'] = __serialized_case_information(citation_data)
    return payload


def __petitioner_payload_without_case_info(data, benefit_files_data):
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

    request_params_without_case_info = {
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
            "isBenefitsProof": len(benefit_files_data) == 0,
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
    return request_params_without_case_info


def __serialized_case_information(case_information):
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

    return {
        "caseNumber": case_information.get('caseNumber'),
        "citationDocumentId": case_information.get('documentid'),
        "citationNumber": case_information.get('citationNumber'),
        "civilAssessFee": case_information.get('civilAssessFee', 0) > 0,
        "county": case_information.get('county'),
        "fullName": case_information.get('firstName', '') + ' ' + case_information.get('lastName', ''),
        "totalDueAmt": case_information.get('totalDueAmt'),
        "violationDate": case_information.get('charges', [])[0].get('violationDate'),
        "violationDescription": "\n".join(violDescriptions),
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
