def active_language():
    return get_language_label(lang)


def get_language_label(localeString):
    language_labels = dict(
        'en': 'English',
        'es': 'Español',
        'zh-s': '简体中文',
        'zh-t': '繁体中文'
    )
    return language_labels[localeString]
