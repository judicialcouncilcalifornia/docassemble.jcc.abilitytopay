import requests
import calendar
import time
import json
import dateutil.parser
import datetime
import hashlib
from docassemble.base.util import *
from azure.storage.blob import BlockBlobService

AD_URL = "https://login.microsoftonline.com/a2pca.onmicrosoft.com/oauth2/token"
CITATION_LOOKUP_URL = 'https://a2papi.azurewebsites.net/api/case/citation'
CASE_LOOKUP_URL = 'https://a2papi.azurewebsites.net/api/case/cases'
SUBMIT_URL = 'https://a2papi.azurewebsites.net/api/request'

def fetch_citation_data(citation_number, county):
    citation_params = {
            'num': citation_number,
            'county': county
    }
    res = __do_request(CITATION_LOOKUP_URL, citation_params)
    return __format_response(res)

def fetch_case_data(first_name, last_name, dob, drivers_license, county):
    case_params = {
            'firstName': first_name,
            'lastName': last_name,
            'dateOfBirth': "%s/%s/%s" % (dob.month, dob.day, dob.year),
            'driversLicense': drivers_license,
            'county': county
    }
    res = __do_request(CASE_LOOKUP_URL, case_params)
    return __format_response(res)

def date_from_iso8601(date_string):
    return dateutil.parser.parse(date_string).date()

def format_money(money_string):
    return '${:,.2f}'.format(money_string)

def __format_response(response, request_body=None):
    data = {}
    data['response_code'] = response.status_code

    if response.ok:
        data['data'] = response.json()
        data['success'] = True
        data['error'] = None

        if request_body:
            data['request_body'] = request_body
    else:
        data['data'] = {}
        data['success'] = False
        data['error'] = response.text

    return data

def __do_request(url, params):
    oauth_params = {
            'resource': '3b347c8c-3faa-4331-8273-a5f575997d4e',
            'grant_type': 'client_credentials',
            'client_id': __get_a2p_config()["client_id"],
            'client_secret': __get_a2p_config()["client_secret"],
            'scope': 'openid 3b347c8c-3faa-4331-8273-a5f575997d4e'
    }
    r = requests.post(AD_URL, oauth_params)
    data = r.json()
    access_token = data['access_token']

    headers = { 'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json' }
    return requests.post(url, data=None, json=params, headers=headers)

def __get_a2p_config():
    return get_config('a2p')

def __submit_image_from_url(url):
    blob_service = BlockBlobService(account_name='a2pca', account_key=__get_a2p_config()['blob_account_key'])
    image_body = requests.get(url).content
    filename = 'a2p_daupload_' + hashlib.sha224(image_body).hexdigest()
    blob_service.create_blob_from_bytes('attachments', filename, image_body)

    return {
            "fileName": filename,
            "blobName": filename,
            "size": len(image_body)
            }

def build_submit_payload(data, attachment_urls):
    benefit_files_data = []

    for url in attachment_urls:
        log("Uploading file: %s" % url)
        image_meta = __submit_image_from_url(url)
        benefit_files_data.append(image_meta)

    no_proof_fields = [
        'calfresh_no_proof',
        'medi_cal_no_proof',
        'ssi_no_proof',
        'ssp_no_proof',
        'cr_ga_no_proof',
        'ihss_no_proof',
        'tanf_no_proof'
        'cal_works_no_proof',
        'capi_no_proof',
    ]

    no_docs_upload_comments = ", ".join([data.get(field + '_reason') for field in no_proof_fields if data.get(field + '_reason')])

    case_information = data.get('case_information')

    benefits = data.get('benefits', {}).get('elements', {})
    no_benefits = True
    for benefit_name in ['cal_fresh', 'ssi', 'ssp', 'medi_cal', 'cr_ga', 'ihss', 'cal_works', 'tanf', 'capi', 'other']:
        if benefits.get(benefit_name):
            no_benefits = False

    submitted_on = datetime.datetime.now().isoformat()

    on_other_benefits = benefits.get('other', False)
    other_benefits_desc = None
    if on_other_benefits:
        other_benefits_desc = data.get('other_benefits_name')
        no_benefits = False

    violDescriptions = []
    idx = 0
    for desc in case_information.get('charges', {}):
        if desc.get('violationDescription'):
            idx += 1
            violDescriptions.append("Count %s: %s" % (idx, desc.get('violationDescription')))

    additional_requests = data.get('additional_requests', {}).get('elements', {})

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
            "onTANF": benefits.get('tanf', False),
            "onCAPI": benefits.get('capi', False),
            "benefitFiles": benefit_files_data,
            "rent": data.get('monthly_rent'),
            "mortgage": data.get('mortgage'),
            "phone": data.get('phone_bill'),
            "food": data.get('food'),
            "insurance": data.get('insurance'),
            "isBenefitsProof": len(attachment_urls) > 0,
            "isCivilAssessWaiver": False,
            "clothes": data.get('clothing'),
            "childSpousalSupp": data.get('child_spousal_support'),
            "carPayment": data.get('transportation'),
            "utilities": data.get('utilities'),
            "otherExpenses": [],
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
            "noDocsToUploadComments": no_docs_upload_comments,
            "isDeclare": True,
            "onOtherBenefits": on_other_benefits,
            "onOtherBenefitsDesc": other_benefits_desc,
        },
        "caseInformation": {
            "caseNumber": case_information.get('caseNumber'),
            "citationDocumentId": case_information.get('documentid'),
            "citationNumber": case_information.get('citationNumber'),
            "civilAssessFee": case_information.get('civilAssessFee'),
            "county": data.get('county'),
            "fullName": case_information.get('firstName', '') + ' ' + case_information.get('lastName', ''),
            "totalDueAmt": case_information.get('totalDueAmt'),
            "violationDate": case_information.get('charges', [])[0].get('violationDate'),
            "violationDescription": " / ".join(violDescriptions),

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
            "difficultyToVisitCourtDueTo": ",".join([k for k,v in data.get('why_difficult', {}).get('elements', {}) if v]),
        },
        "submittedById": "0",
        "judgment": "Submitted",
        "submittedByEmail": data.get('email'),
        "submittedOn": submitted_on,
        "needMoreInformation": [],
        "toolRecommendations": [],
        "judicialOrder": [],
        "auditInformation": [],
        "__v": 0
    }
    return request_params


def submit_interview(data, attachment_urls=[], debug=False):
    params = build_submit_payload(data, attachment_urls)
    log("Submitting Payload: %s" % params)
    res = __do_request(SUBMIT_URL, params)

    if debug:
        return __format_response(res, params)
    else:
        return __format_response(res)


#print(fetch_citation_data('CT98966', 'Tulare'))
# print(fetch_case_data('john', 'doe', '11/26/1985', '12345', 'Santa Clara'))
#print(submit_interview({ 'citationNumber': 1234 }))

