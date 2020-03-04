import dateutil.parser

def date_from_iso8601(date_string):
    return dateutil.parser.parse(date_string).date()

def format_money(money_string):
    return '${:,.2f}'.format(money_string)
