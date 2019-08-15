#!/usr/bin/env python3
import sys
sys.path.append('../docassemble/jcc/abilitytopay/')

from translations import _translations


if len(sys.argv) < 2:
    print('Usage: ./validate_translations.py <lang>')
else:
    lang = sys.argv[1]


print('Looking for missing {} strings'.format(lang))
for key, translation_dict in _translations.items():
    if lang not in translation_dict:
        print('No {} translation for {}\n'.format(lang, key))
    if translation_dict[lang] == '':
        print('No {} translation for {}'.format(lang, key))
        print('en: {}\n'.format(translation_dict['en']))
