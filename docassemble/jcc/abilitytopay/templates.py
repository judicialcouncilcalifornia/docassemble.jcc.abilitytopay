from docassemble.base.util import encode_name
import json

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
