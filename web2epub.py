#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# web2pub.py - generate epubs and json file for use with whatabagacack
# Copyright (C) 2023  Chris Clark
"""Python 2 or Python 3

Sample Usage:

    web2epub.py https://en.wikipedia.org/wiki/EPUB

"""


import json
import logging
import os
import sqlite3
import sys

import w2d  # https://github.com/clach04/w2d

import whatabagacack_db

#w2d.log.setLevel(logging.DEBUG)


log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(level=logging.DEBUG)


def scrape_and_save_one(c, rowid, url):
    """TODO doc environment variables that cause side effects
        cache dir ? W2D_CACHE_DIR, currently handled by caller, e.g. scrape_and_save()
        output dir - current directory, also handled by caller
    """
    # TODO call w2d.process_page() instead
    #result_metadata = w2d.dump_url(url, output_format=w2d.FORMAT_EPUB, filename_prefix='%d_' % rowid)  # TODO more options (e.g. skip readability, etc.)
    result_metadata = w2d.process_page(url, output_format=w2d.FORMAT_HTML, extractor_function=w2d.extractor_raw, filename_prefix='%d_' % rowid)  # DEBUG

    title = result_metadata['title']
    epub_filename = result_metadata['filename']

    # Wallabag like (subset) meta data)
    # Bare minimum to allow wallabag-client to work, also works for KoReader
    # TODO more metadata
    entry_metadata = {
        "id": rowid,
        "tags": [],
        "url": url,
        "title": title,
        "content": None,
        "is_archived": 0,
        "is_starred": 0
    }
    bind_params = (epub_filename, json.dumps(entry_metadata), rowid)
    c.execute('UPDATE entries SET epub = ?, wallabag_entry = ? WHERE rowid = ?', bind_params)

def scrape_and_save(database_details):
    w2d.safe_mkdir(w2d.cache_dir)  # i.e. W2D_CACHE_DIR - TODO this could be better
    url_db = whatabagacack_db.UrlDb(database_details)

    url_db._connect()
    c = url_db._db.cursor()
    c_update = url_db._db.cursor()

    c.execute('SELECT count(rowid) FROM entries WHERE epub is NULL')
    row = c.fetchone()
    total = row[0]  # total number of entries that match
    log.info('%d entries to scrape and save', total)
    # Potentially log progress

    counter = 0
    converted_counter = 0
    c.execute('select rowid, url from entries where epub is NULL')
    row = c.fetchone()
    while row:
        rowid, url = row
        log.info('%d of %d %d %r', counter, total, rowid, url)
        try:
            scrape_and_save_one(c_update, rowid, url)
            converted_counter += 1
        except:
            log.error('Error scrape_and_save_one', exc_info=1)  # include traceback
        counter += 1
        row = c.fetchone()
    log.info('%d entries converted out of %d', converted_counter, total)

    c.close()
    c_update.close()
    url_db.commit()
    url_db._disconnect(commit=True)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    urls = argv[1:]  # no argument processing (yet)
    print(urls)

    entries_config_filename = os.environ.get('WEB_SITE_METADATA_FILENAME', 'entries.json')
    database_details = os.environ.get('WEB_SITE_DATABASE', 'web2epub.sqlite3')
    print('Connecting to database %r' % database_details)
    db = sqlite3.connect(database_details)
    c = db.cursor()
    """
        entry_metadata = {
            "id": id,
            "tags": [],
            "url": url,
            "title": title,
            "content": None,
            "is_archived": 0,
            "is_starred": 0
        }
        all_meta_data[id] = {
            'wallabag_entry': entry_metadata,
            'epub': epub_filename,
        }

    """
    # TODO tags at some point
    # TODO FTS? only needed if want to query text
    # NOTE sqlite3 defaults to 'rowid' identity column
    """rowid maps to id, the rest of the "top" map exactly to wallabag entry
    wallabag_entry is json and the entire wallabag entry
    epub is the epub filename

    TODO Allow to be stored in database and seperate worker to perform scrape/epub-conversion?
    whatbagacack should then exclude epub IS NULL and wallabag_entry IS NULL rows
    """
    # FIXME use UrlDb()
    c.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        rowid INTEGER PRIMARY KEY ASC,
        url TEXT UNIQUE NOT NULL,
        is_archived INT NOT NULL,  /* Wallabag is_archived metadata */

        epub TEXT NULLABLE,  /* if NULL, not scraped? consider making UNIQUE It should be unique, but does this need to be enforced in the database (with index overhead)? */
        wallabag_entry TEXT  /* if NULL, not scraped? */
        )
    ''')

    # TODO setup W2D_CACHE_DIR
    all_meta_data = {}
    converted_counter = 0
    for id, url in enumerate(urls, 1):
        print((id, url))
        """
        dumb_title = url.replace('https', '').replace('http', '').replace('ftp', '').replace(':', '').replace('//', '').replace('/', ' ')
        dumb_filename = dumb_title.replace(' ', '_') + '.epub'  # FIXME this won't match what w2d does
        print('\t%s' % dumb_title)
        print('\t%s' % dumb_filename)
        """

        # TODO check does not exist already
        bind_params = (url,)
        c.execute('SELECT rowid FROM entries WHERE url = ?', bind_params)
        rows = c.fetchall()
        print('rows %r' % rows)
        if rows:
            print('Skipping already in db id %r, for url %r' % (id, url))  # FIXME logging.info - also options for force (re-fresh, which would likely also need existing epub to be deleted)
            continue

        bind_params = (url, 0)
        c.execute('insert into entries (url, is_archived) values (?, ?)', bind_params)
        id = c.lastrowid

        # TODO call w2d.process_page() instead
        result_metadata = w2d.dump_url(url, output_format=w2d.FORMAT_EPUB, filename_prefix='%d_' % id)  # TODO more options (e.g. skip readability, etc.)
        title = result_metadata['title']
        epub_filename = result_metadata['filename']

        # Wallabag like (subset) meta data)
        # Bare minimum to allow wallabag-client to work, also works for KoReader
        # TODO more metadata
        entry_metadata = {
            "id": id,
            "tags": [],
            "url": url,
            "title": title,
            "content": None,
            "is_archived": 0,
            "is_starred": 0
        }
        #bind_params = (url, 0, json.dumps(entry_metadata), epub_filename)
        #c.execute('insert into entries (url, is_archived, wallabag_entry, epub) values (?, ?, ?, ?)', bind_params)
        bind_params = (epub_filename, json.dumps(entry_metadata), id)
        c.execute('UPDATE entries SET epub = ?, wallabag_entry = ? WHERE rowid = ?', bind_params)
        entry_metadata['id'] = id
        all_meta_data[id] = {
            'wallabag_entry': entry_metadata,
            'epub': epub_filename,
        }
        converted_counter += 1



    """
    print(all_meta_data)
    print(json.dumps(all_meta_data, indent=4))  # TODO dump to a file
    """

    print('Converted %d out of %d URLs' % (converted_counter, -1))
    print('COMMITing to database %r' % database_details)
    db.commit()
    print('Writing to %r' % entries_config_filename)
    f = open(entries_config_filename, 'wb')
    f.write(json.dumps(all_meta_data, indent=4).encode('utf-8'))
    f.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
