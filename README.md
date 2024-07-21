# ❓👜💩❗ What A Bag A Cack

Home page https://github.com/clach04/whatabagacack

If you stumbled on this project in relation to Wallabag, don't use this!
Use Wallabag instead. See alternatives section.

Experimental (incomplete) Wallabag API Server that runs under Python 3 and 2.
Runs under Microsoft Windows and Linux (expected to run under Mac, but untested).

Uses https://github.com/clach04/w2d for epub generation

  * [Overview](#overview)
  * [Status](#status)
  * [resources](#resources)
    + [Test / Sample URLs](#test---sample-urls)
  * [What is this good for?](#what-is-this-good-for-)
  * [Usage](#usage)
    + [Quick Start Server](#quick-start-server)
    + [Usage Server](#usage-server)
    + [Usage Dumb Scraper](#usage-dumb-scraper)
  * [Alternatives](#alternatives)
    + [Content Saving](#content-saving)
    + [URL / Bookmarking](#url---bookmarking)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


## Overview

What a 👜 of 💩.

Remotely similar to https://github.com/clach04/fake-shaarli-server
make something looking like something else, a bridge/gateway/proxy.

Aim to support a subset of the [Wallabag REST API](https://app.wallabag.it/api/doc/) used by:

  * https://github.com/artur-shaik/wallabag-client
      * https://shaik.link/posts/wallabag-client/features/
      * `python -m pip install wallabag-client`
  * https://github.com/koreader/koreader
      * https://github.com/koreader/koreader/wiki/Wallabag
      * https://github.com/koreader/koreader/tree/master/plugins/wallabag.koplugin
      * https://github.com/clach04/wallabag2.koplugin
          * https://github.com/koreader/koreader/issues/9151 - wallabag plugin show progress for downloading article
          * https://github.com/koreader/koreader/issues/10738 - wallabag performance slower than it needs to be
  * Stretch goals
      * Javascript bookmarklet (clone) `javascript:(function(){var url=location.href||url;var wllbg=window.open('https://app.wallabag.it/bookmarklet?url=' + encodeURIComponent(url),'_blank');})();`
      * Official [Android app](https://github.com/wallabag/android-app)
          * https://f-droid.org/app/fr.gaulupeau.apps.InThePoche
          * https://play.google.com/store/apps/details?id=fr.gaulupeau.apps.InThePoche
      * [Browser extensions/plugin/addons](https://github.com/wallabag/wallabagger)
          * https://addons.mozilla.org/firefox/addon/wallabagger/
          * https://chrome.google.com/webstore/detail/wallabagger/gbmgphmejlcoihgedabhgjdkcahacjlj
      * alternative android apphttps://github.com/casimir/frigoligo
      * [Bookmarklet extension](https://addons.mozilla.org/en-US/firefox/addon/wallabaggerini/) https://github.com/Johennes/wallabaggerini - https://github.com/clach04/whatabagacack/issues/16
      * alternative API, extension support https://github.com/kyoheiu/leaf/tree/main/extension/firefox

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

### Quick Start Server

Also see:

  * [Usage Dumb Scraper](#usage-dumb-scraper)
  * [Usage Server](#usage-server)


Install bare minimum / recommend dependencies:

    python -m pip install -e git+https://github.com/clach04/w2d.git#egg=w2d
    # manually install pandoc https://pandoc.org/installing.html
    sudo apt-get install
    # install / run Postlight (nee Mercury) Parser web API (locally) from https://github.com/HenryQW/mercury-parser-api
    docker run -p 3000:3000 -d wangqiru/mercury-parser-api

Scrape and launch server

    mkdir archived_sites
    cd archived_sites
    python ../web2epub.py https://en.wikipedia.org/wiki/EPUB
    python ../whatabagacack.py


    ## demo read meta data
    curl http://localhost:8000/api/entries


### Usage Server

    set WEB_SITE_DATABASE=C:\code\py\w2d\web2epub.sqlite3
    set WEB_EPUB_DIRECTORY=C:\code\py\w2d\

    export WEB_SITE_DATABASE=/code/py/w2d/web2epub.sqlite3
    export WEB_EPUB_DIRECTORY=/code/py/w2d

    python whatabagacack.py

NOTE no longer expects `entries.json` to exist and be in correct format, defaults to sqlite3 database. Code still present for json entries.
Override file name with operating system environment variable `WEB_SITE_METADATA_FILENAME` to pathname of json file.

DEBUG note, set operating system environment variable `OVERRIDE_EPUB_FILENAME` to full pathname to an epub to always return that one file.


### Usage Dumb Scraper

    set WEB_SITE_DATABASE=C:\code\py\w2d\web2epub.sqlite3
    export WEB_SITE_DATABASE=/code/py/w2d/web2epub.sqlite3

    python web2epub.py [list of urls]

Example:

    python web2epub.py https://en.wikipedia.org/wiki/EPUB
    # NOTE requires manually copy/pasting json into entries.json (or some other name)

## Alternatives

### Content Saving

  * Wallabag either self hosted or subscription service - great team, this is the least effort option available and very reasonably priced. The Android app is very decent.
  * https://github.com/LordEidi/wombag - Written in Go, also offers Wallabag API
  * https://github.com/go-shiori/shiori excellent scraping and readability support with full archive as well
  * https://codeberg.org/readeck/readeck
  * https://github.com/dullage/url2kindle
  * https://github.com/omnivore-app/omnivore (as of 2023, not possible to self host due to GCO requirements). Has an android app.
  * https://codeberg.org/readeck/readeck - Go which has a neat web browser extension which can use the browser to scrape (then upload) instead of the server. Supports multiple articles/collections in a single epub. Also includes an OPDS server
  * https://github.com/OpenArchive
  * https://github.com/ArchiveBox/ArchiveBox - Python
      * https://github.com/ArchiveBox/archivebox-proxy - MITM proxy to record browsing sessions
      * https://github.com/ArchiveBox/archivebox-spreadsheet-bot - feed URLs from a Spreadsheet/Google-Sheet
      * https://github.com/ArchiveBox/readability-extractor - command lin node tool
  * https://github.com/linkwarden/linkwarden - TypeScript

### URL / Bookmarking

  * https://github.com/arunk140/portall - Python Django (untested)
  * https://github.com/rumca-js/Django-link-archive (untested)
  * [LinkDing](https://github.com/sissbruecker/linkding) - Python Django
  * [Sharli](https://github.com/shaarli/Shaarli) - PHP, annoying storage (serializes entire list on each save)
  * https://github.com/Kovah/LinkAce - PHP (untested)


### Client Tools and Browser Extensions

  * https://github.com/artur-shaik/wallabag-client - see whatabagacack features
  https://github.com/casimir/frigoligo - wallabag (android)
  * https://github.com/ArchiveBox/archivebox-browser-extension
