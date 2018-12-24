import requests
import calendar
import time
import json
import dateutil.parser
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
            'dateOfBirth': dob,
            'driversLicense': drivers_license,
            'county': county
    }
    res = __do_request(CASE_LOOKUP_URL, case_params)
    return __format_response(res)

def date_from_iso8601(date_string):
    return dateutil.parser.parse(date_string).date()

def format_money(money_string):
    return '${:,.2f}'.format(money_string)

def __format_response(response):
    data = {}
    data['response_code'] = response.status_code

    if response.ok:
        data['data'] = response.json()
        data['success'] = True
        data['error'] = None
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

    headers = { 'Authorization': 'Bearer ' + access_token }
    return requests.post(url, params, None, headers=headers)

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

def submit_interview(data, attachment_urls=[]):
    benefitFilesData = []

    for url in attachment_urls:
        image_meta = __submit_image_from_url(url)
        benefitFilesData.append(image_meta)

    request_params = {
        "requestStatus": "Submitted",
        "petition": {
            "noBenefits": data.get('benefits'),
            "onFoodStamps": data.get('cal_fresh'),
            "onSuppSecIncome": data.get('ssi'),
            "onSSP": data.get('ssp'),
            "onMedical": data.get('medi_cal'),
            "onCountyRelief": data.get('cr_ga'),
            "onIHSS": data.get('ihss'),
            "onCalWorks": data.get('cal_works'),
            "onTANF": data.get('tanf'),
            "onCAPI": data.get('capi'),
            "benefitFiles": benefitFilesData,
            "rent": data.get('monthly_rent'),
            "mortgage": data.get('mortgage'),
            "phone": data.get('phone_bill'),
            "food": data.get('food'),
            "insurance": data.get('insurance'),
            "clothes": data.get('clothing'),
            "childSpousalSupp": data.get('child_spousal_support'),
            "carPayment": data.get('transportation'),
            "utilities": data.get('utilities'),
            "otherExpenses": [],
            "isMoreTimeToPay": data.get('extension'),
            "isPaymentPlan": data.get('payment_plan'),
            "isReductionOfPayment": True,
            "isCommunityService": data.get('community_service'),
            #"isCivilAssessWaiver": ,
            "isOtherRequest": False,
            #"otherRequestDesc": null,
            "selectAllRights": True,
            "representByAttorneyRight": True,
            "speedyTrialRight": True,
            "presentEvidenceRight": True,
            "testifyUnderOathRight": True,
            "remainSilentRight": True,
            "isPleadGuilty": True,
            "isPleadNoContest": False,
            "supportingFiles": [],
            #"noDocsToUploadReason": "I got evicted",
            #"noDocsToUploadComments": "comments",
            "isDeclare": True
        },
        "caseInformation": {
            "citationNumber": data.get('citation_number'),
            "county": data.get('county'),
        },
        "benefitsStatus": True,
        "defendantInformation": {
            "incomeAmount": data.get('income'),
            "incomeFrequency": data.get('frequency'),
            "totalFamilyMembers": data.get('residents'),
        },
        "survey": {
            "isAddressedTrafficMatter": data.get('tool_helpful'),
            "willYouVisitCourt": data.get('able_in_person'),
            "difficultyToVisitCourtDueTo": data.get('why_difficult'),
        },
        "submittedById": "0",
        "judgment": "Submitted",
        "submittedByEmail": "temp@temp.com",
        "submittedOn": {
            "$date": calendar.timegm(time.gmtime()),
        },
        "needMoreInformation": [],
        "toolRecommendations": [],
        "judicialOrder": [],
        "auditInformation": [],
        "__v": 0
    }
    res = __do_request(SUBMIT_URL, json.dumps(request_params))
    return __format_response(res)


# print(fetch_citation_data('CT98966', 'Tulare'))
# print(fetch_case_data('john', 'doe', '11/26/1985', '12345', 'Santa Clara'))
# print(submit_interview({ 'citationNumber': 1234 }))
