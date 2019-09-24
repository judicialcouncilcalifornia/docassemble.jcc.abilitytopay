#!/usr/bin/env python

import sys

VERSION = sys.argv[1]

version_file_path = "./docassemble/jcc/abilitytopay/data/static/version.js"
version_string = """
//
// This file is re-generated automatically by write_version.py
//

var A2P_PUBLIC_UI_VERSION='{0}';
console.log('ATP Public UI ' + A2P_PUBLIC_UI_VERSION);
""".format(VERSION)

with open(version_file_path, "w+") as version_file:
    version_file.write(version_string)

print("Wrote version {0} to {1}".format(VERSION, version_file_path))
