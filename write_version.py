#!/usr/bin/env python

import sys

VERSION = sys.argv[1]

version_file_path = "./docassemble/jcc/abilitytopay/data/static/version.js"
version_string = """
var A2P_PUBLIC_UI_VERSION='{0}';
console.log('Ability to Pay ' + A2P_PUBLIC_UI_VERSION);
""".format(VERSION)

with open(version_file_path, "w+") as version_file:
  version_file.write(version_string)

print("Wrote version {0} to {1}".format(VERSION, version_file_path))
