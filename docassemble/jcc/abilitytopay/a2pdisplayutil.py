
import re
from docassemble.base.util import user_info

# this returns the interview filename and package for use in links

def interview_in_package(yaml_filename):
  current_filename = user_info().filename
  if current_filename.startswith('docassemble.playground'):
    return re.sub(r'(.*:).*', r'\1' + yaml_filename, current_filename)
  return re.sub(r'(.*/).*', r'\1' + yaml_filename, current_filename)
