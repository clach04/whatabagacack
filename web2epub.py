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
import sys

import w2d  # https://github.com/clach04/w2d


def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' % (sys.version, sys.platform))

    urls = argv[1:]  # no argument processing (yet)
    print(urls)

    # TODO setup W2D_CACHE_DIR
    all_meta_data = {}
    for id, url in enumerate(urls, 1):
        print((id, url))
        """
        dumb_title = url.replace('https', '').replace('http', '').replace('ftp', '').replace(':', '').replace('//', '').replace('/', ' ')
        dumb_filename = dumb_title.replace(' ', '_') + '.epub'  # FIXME this won't match what w2d does
        print('\t%s' % dumb_title)
        print('\t%s' % dumb_filename)
        """

        result_metadata = w2d.dump_url(url, output_format=w2d.FORMAT_EPUB)  # TODO more options (e.g. skip readability, etc.)
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
        all_meta_data[id] = {
            'wallabag_entry': entry_metadata,
            'epub': epub_filename,
        }
    print(all_meta_data)
    print(json.dumps(all_meta_data, indent=4))  # TODO dump to a file

    return 0


if __name__ == "__main__":
    sys.exit(main())
