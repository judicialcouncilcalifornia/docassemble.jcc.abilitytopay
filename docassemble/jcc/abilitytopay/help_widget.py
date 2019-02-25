def help_tip(help_text):
    return '<span class="help-tip">{0}</span>'.format(help_text)

def help_widget(disclosure_text, help_heading, help_text):
    return '<a href="#" class="help-widget">{0}</a><div class="help-widget-body"><h5>{1}</h5>{2}</div>'.format(disclosure_text, help_heading, help_text)
