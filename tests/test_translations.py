import os
import sys
import re

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, '../docassemble/jcc/abilitytopay/'))

from translations import _translations

# We check to make sure that translations exist for all languages
# in ACTIVE_LANGUAGES
ACTIVE_LANGUAGES = ['en', 'es']


def get_interview_keys():
    interview_path = os.path.join(cwd, '../docassemble/jcc/abilitytopay/data/questions/questions.yml')
    with open(interview_path, 'r') as interview:
        interview_text = interview.read()
    return re.findall(
        'get_translation\(\'([a-zA-Z_\s]+)\', lang\)', interview_text
    )


def test_missing_translation_keys():
    missing_entries = [
        key
        for key in get_interview_keys()
        if key not in _translations
    ]
    assert len(missing_entries) == 0, \
        'These keys appear in questions.yml but are missing entries in translations.py: {}'.format(', '.join(missing_entries))


def test_missing_translation_languages():
    missing_translations = [
        key
        for key in get_interview_keys()
        if key in _translations and
        any([(lang not in _translations[key] or _translations[key][lang] == '') for lang in ACTIVE_LANGUAGES])
    ]
    assert len(missing_translations) == 0, \
        'These keys are missing translations in one or more languages: {}'.format(', '.join(missing_translations))
