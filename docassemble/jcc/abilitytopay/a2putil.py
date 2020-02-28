import dateutil.parser

import re
from docassemble.base.util import user_info


def date_from_iso8601(date_string):
    return dateutil.parser.parse(date_string).date()

def format_money(money_string):
    return '${:,.2f}'.format(money_string)

    # this returns the interview filename and package for use in links

def interview_in_package(yaml_filename):
  current_filename = user_info().filename
  if current_filename.startswith('docassemble.playground'):
    return re.sub(r'(.*:).*', r'\1' + yaml_filename, current_filename)
  return re.sub(r'(.*/).*', r'\1' + yaml_filename, current_filename)
