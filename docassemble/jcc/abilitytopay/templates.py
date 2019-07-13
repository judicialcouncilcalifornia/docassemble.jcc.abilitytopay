import json
from docassemble.base.util import encode_name
from .a2putil import format_money, date_from_iso8601
from .translations import get_translation

def a2p_file_input(file_variable_name):
  return """
<div class="a2p-file-upload-container">
  <div class="a2p-upload-complete"><span class="a2p-upload-complete-icon fas fa-check-circle"></span>Upload Complete</div>
  <img class="a2p-image-preview" />
  <div class="a2p-file-upload-buttons">
    <label class="a2p-file-upload-button btn btn-primary btn-block" for="{encoded_variable_name}">
      <span class="a2p-file-upload-label">Add a photo</span> <span style="position: relative; top: 2px; margin-left: 6px; font-size: 20px" class="fas fa-camera"></span>
      <input class="a2p-file-input" type="file" name="{encoded_variable_name}" id="{encoded_variable_name}">
      <input type="hidden" name="_files" value="{encoded_list}"/>
    </label>
    <div class="a2p-file-remove-button btn btn-secondary" style="display: none"><span class="fas fa-trash-alt"></span></div>
  </div>
</div>
""".format(
  encoded_variable_name=encode_name(file_variable_name),
  encoded_list=encode_name(json.dumps([encode_name(file_variable_name)]))
)

def citation_info_card(case, lang):
  return """
<div class='info-card'>
  <h4>{citationNumber}</h4>
  <dl>
    <dt>{name_label}</dt><dd>{name}</dd>
    <dt>{citation_number_label}</dt><dd>{citationNumber}</dd>
    <dt>{county_label}</dt><dd>{county}</dd>
    <dt>{violation_date_label}</dt><dd>{violationDate}</dd>
    <dt>{total_due_label}</dt><dd>{totalDue}</dd>
  </dl>
</div>
""".format(
  name_label=get_translation('name', lang),
  citation_number_label=get_translation('citation_number', lang),
  county_label=get_translation('county', lang),
  violation_date_label=get_translation('violation_date', lang),
  total_due_label=get_translation('total_due', lang),
  name=case['firstName'] + " " + case['lastName'],
  county=case['county'],
  citationNumber=case['citationNumber'],
  violationDate=date_from_iso8601(case['charges'][0]['violationDate']),
  totalDue=format_money(case['totalDueAmt'])
)
