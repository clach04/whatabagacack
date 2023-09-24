#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""

Sample Usage

    set TMP_DB_NAME=test_archive_dir\test_db.sqlite3
    del %TMP_DB_NAME%

    python test.py
    "C:\Program Files\SQLite ODBC Driver for Win64\sqlite3.exe" %TMP_DB_NAME% .dump
    dir test_archive_dir

"""

# using w2d test server pages


import json
import logging
import os
import sqlite3
import sys

import whatabagacack_db
import web2epub


#w2d.log.setLevel(logging.DEBUG)
web2epub.log.setLevel(logging.INFO)

def doit(filename=None):
    """FIXME
        - cache dir
        - archive dir
        - parser - raw / postlight
        - format
        - converter - setting W2D_EPUB_TOOL=pandoc has no effect with w2d.process_page()
    """
    #import pdb ; pdb.set_trace()
    if filename:
        f = open(filename, 'r')
        url_list_str = f.read()
        f.close()
    else:
        url_list_str = """
http://localhost:8000/one.html
http://localhost:8000/two.html
http://localhost:8000/sub_dir/three.html
"""
    archive_dir = os.environ.get('ARCHIVE_DIR', 'test_archive_dir')
    database_details = os.environ.get('ARCHIVE_DB', 'test_db.sqlite3')  # relative to ARCHIVE_DIR
    orig_cwd = os.path.abspath(os.path.normpath(os.getcwd()))

    web2epub.w2d.safe_mkdir(archive_dir)
    os.chdir(archive_dir)
    url_db = whatabagacack_db.UrlDb(database_details, autocommit=False)
    url_db._connect()

    for line in url_list_str.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):  # comment
            continue
        print('%s' % line)
        rowid = url_db.url_add(line)
    #import pdb ; pdb.set_trace()
    url_db.commit()
    url_db._disconnect()

    web2epub.scrape_and_save(database_details)
    os.chdir(orig_cwd)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))
    try:
        filename = argv[1]
    except IndexError:
        filename = None
    doit(filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())
