# whatabagacack

Home page https://github.com/clach04/whatabagacack

If you stumbled on this project in relation to Wallabag, don't use this!
Use Wallabag instead. Or perhaps:

  * https://github.com/LordEidi/wombag - Written in Go

Experimental (incomplete) Wallabag API Server that runs under Python 3 and 2.

- [whatabagacack](#whatabagacack)
  * [Overview](#overview)
  * [Status](#status)
  * [resources](#resources)
    + [Test / Sample URLs](#test---sample-urls)
  * [What is this good for?](#what-is-this-good-for-)
  * [Usage](#usage)
    + [Usage Server](#usage-server)
    + [Usage Dumb Scraper](#usage-dumb-scraper)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


## Overview

What a 👜 of 💩.

Remotely similar to https://github.com/clach04/fake-shaarli-server
make something looking like something else, a bridge/gateway/proxy.

Aim to support a subset of the [Wallabag REST API](https://app.wallabag.it/api/doc/) used by:

  * https://github.com/artur-shaik/wallabag-client
      * `python -m pip install wallabag-client`
  * https://github.com/koreader/koreader
      * https://github.com/koreader/koreader/wiki/Wallabag
      * https://github.com/koreader/koreader/tree/master/plugins/wallabag.koplugin
      * https://github.com/clach04/wallabag2.koplugin


## Status

  * Zero authentication support, server accepts any client without any auth check
  * Handles enough for `wallabag list` to work
  * Handles enough for `wallabag export --format epub ID_HERE` to work - either file specified in json "model" or via override OVERRIDE_EPUB_FILENAME os env
  * Handles enough for KoReader Wallabag plugin to list and then download epub entries
  * Can generate metadata with epubs (epub2) from a list of URLs

## resources

* https://github.com/search?q=repo%3Awallabag%2Fwallabag%20%40route&type=code
* https://app.wallabag.it/api/doc
* https://github.com/wallabag/doc/blob/master/en/developer/api/methods.md **old** still useful and in easy to read form
* https://github.com/wallabag/doc/blob/master/en/developer/api/oauth.md
* https://github.com/Strubbl/wallabago as a nice short list of API endpoints

### Test / Sample URLs

    https://en.wikipedia.org/wiki/EPUB
    https://en.wikipedia.org/wiki/Fb2
    https://en.wikipedia.org/wiki/FBReader
    https://en.wikipedia.org/wiki/Web_scrape
    https://en.wikipedia.org/wiki/Archive.org
    https://en.wikipedia.org/wiki/Swamp_wallaby
    https://en.wikipedia.org/wiki/Laser_Chess
    https://en.wikipedia.org/wiki/Lazer_Maze
    https://en.wikipedia.org/wiki/Deflektor
    https://en.wikipedia.org/wiki/Atomic_chess
    https://en.wikipedia.org/wiki/Stratomic

    https://en.wikipedia.org/wiki/Chess_piece
    https://en.wikipedia.org/wiki/Chess_symbols_in_Unicode

1. NOTE - the later 2 cause problems for pypub3 - https://github.com/imgurbot12/pypub (which is why pypub3 is **not** used).
2. NOTE - pypub as of 2023-07-30 can't handle Wikipedia (style) href links correctly.

## What is this good for?

  * For debugging wallabag clients, e.g. KoReader
  * for replacing the Wallabag epub/page-scraper with an alternative one

## Usage

### Usage Server

    set WEB_SITE_DATABASE=C:\code\py\w2d\web2epub.sqlite3
    set WEB_EPUB_DIRECTORY=C:\code\py\w2d\

    export  WEB_SITE_DATABASE=/code/py/w2d/web2epub.sqlite3
    export WEB_EPUB_DIRECTORY=/code/py/w2d

    python whatabagacack.py

NOTE no longer expects `entries.json` to exist and be in correct format, defaults to sqlite3 database. Code still present for json entries.
Override file name with operating system environment variable `WEB_SITE_METADATA_FILENAME` to pathname of json file.

DEBUG note, set operating system environment variable `OVERRIDE_EPUB_FILENAME` to full pathname to an epub to always return that one file.


### Usage Dumb Scraper

    set WEB_SITE_DATABASE=C:\code\py\w2d\web2epub.sqlite3
    export  WEB_SITE_DATABASE=/code/py/w2d/web2epub.sqlite3

    python web2epub.py [list of urls]

Example:

    python web2epub.py https://en.wikipedia.org/wiki/EPUB
    # NOTE requires manually copy/pasting json into entries.json (or some other name)
